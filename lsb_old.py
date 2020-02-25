from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct
import ia636 as ia
import sys
import math
import binascii


bitNroEncode = 0
nroBlocks = 0
messageCode = 1


def unPadding(l, h, img):
	print l,h
	img = img[:h,:l]
	return img

#padding is working, but i wont use it: message on border being cropped when restoring original image dimensions
def zeroPadding(img):
	
	padRight = 8 - (img.size[0] % 8)
	padBottom = 8 - (img.size[1] % 8)
	
	npad = ((0,padBottom),(0,padRight),(0,0))
	
	return np.pad(img, pad_width = npad, mode = 'constant', constant_values = 0)

def blocks8by8(img,xOrigin, yOrigin):
	
	block = np.zeros((8,8));
	
	for y in xrange(yOrigin,yOrigin + 8):
		for x in xrange(xOrigin, xOrigin + 8):
			if img.ndim > 2:
				block[x - xOrigin][y-yOrigin] = img[x][y][0]
			else:
				block[x - xOrigin][y-yOrigin] = img[x][y]
	return block
		
def insertBlock(block,imgMod, yOrigin, xOrigin):
	for lin in xrange(8):
		for col in xrange(8):
			imgMod[lin + yOrigin][col + xOrigin] = block[lin][col]
			
	return imgMod		
		
def is_grey_scale(im):
    w,h = im.size
    for i in range(w):
        for j in range(h):
            r,g,b = im.getpixel((i,j))
            if r != g != b: return False
    return True		



#Funciona!!	
def encodeLSB(imgBlock, data):

	global bitNroEncode
	global matrixTest
	controlBlock = imgBlock.copy()
	
	for lin in xrange(8):
		for col in xrange(8):
			if(len(data) > 0):
				bit = data[:1] #first element from data
				data = data[1:] #removing first element from data
				dataByte = imgBlock[lin][col].astype('int32')
				encodedByte = bin(dataByte)[:-1] + bit
					
				BackUp = imgBlock[lin][col]
				bitNroEncode = bitNroEncode + 1
				if(encodedByte[:1] == '-'):
					imgBlock[lin][col] = (-1)*int(encodedByte[1:],2)
				else:
					imgBlock[lin][col] = int(encodedByte,2)
					
					
	return imgBlock

	
#Funciona!!
def decodeLSB(img):
	message = ''
	cnt = 1
	bitNro = 0 
	
	h = img.shape[0] % 8
	w = img.shape[1] % 8
	
	global messageCode
	print 'image shape (L,C)?'
	print img.shape[0]
	
	for lin in xrange(0,img.shape[0]-h,8):
		for col in xrange(0,img.shape[1]-w,8):
			
			
			b = blocks8by8(img,lin,col)
			
			
			for idx,byte in np.ndenumerate(b):
			
				bit = bin(byte.astype('int32'))[-1:]
				
				encodedByte = byte.astype('int32')
				
				message = message + bit
				bitNro = bitNro + 1
				if message[-16:] == bin(0xFFAA)[2:]:
					messageCode = 0
					print "Message Code"
					print messageCode
					print len(message)
					return message[:-16]
				
			cnt = cnt + 1
			
				
				
	return message	
	
	
def encodeIMG(img, binData):
	# For each 8x8 Block, a dct is made, information is added and idct is made so the image is mounted again
	h = img.shape[0] % 8
	w = img.shape[1] % 8
	base2D = np.zeros_like(img)
	global nroBlocks
	
	for lin in xrange(0,img.shape[0]-h,8):
		for col in xrange(0,img.shape[1]-w,8):
			b = blocks8by8(img,lin, col)
			if (nroBlocks > 0):
				
				encodedBlock = encodeLSB(b.copy(),binData[:64])
				binData = binData[64:]
				b = encodedBlock
				
				nroBlocks = nroBlocks - 1
				
			imgMod = insertBlock(b,base2D,lin,col)
	return imgMod

def Main(argv):
	filename = sys.argv[1]
	img = Image.open(filename)
	
	file = open('alice30.txt','r')
	
	data = file.read()
	
	type = 3
	
	global messageCode
	
	binData = bin(int(binascii.hexlify(data), 16))[2:] + bin(0xFFAA)[2:]
	#print binData
	dataLen =  len(binData)
	print dataLen
	binDataBackUp = binData
	#decoding : 
	n = int('0b'+binData,2)
	#print "decoded: " + binascii.unhexlify('%x' % n)
	
	print img.mode
	
	if(img.mode == "RGBA"):
		R,G,B,A = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		arrayA = np.asarray(A)
		type = 1
	elif(img.mode == "L"):
		arrayL = np.asarray(img)
		type = 2
	else:
		img = img.convert("RGB")
		R,G,B = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		type = 0
	print img.size
	
	#adds zero to the borders so the image can have a interger number of
	#blocks 8x8
	
	
	global nroBlocks
	nroBlocks = math.ceil(dataLen/64.0)
	imgMod = []
	
	w = img.size[0]
	h = img.size[1]
	
	capacity = (w - w%8)*(h - h%8)
	
	print capacity
	
	print 'type = ' + str(type)
	if(type == 2): #Mode L
		if(dataLen > capacity):
			return -1
		else:
			imgMod = encodeIMG(arrayL, binData)
			imgMod = Image.fromarray(imgMod, 'L')
			
	elif(type == 1): #mode RGBA
		if(dataLen > capacity * 4):
			#print 'hi'
			return -1
		else:
			nroLayers = math.ceil(dataLen/float(capacity))
			if(nroLayers == 4):
				print 'nroLayers: ' + str(nroLayers)
				imgModR = encodeIMG(arrayR, binData[:capacity])
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity])
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity])
				binData = binData[capacity:]
			
				imgModA = encodeIMG(arrayA, binData[:capacity])
			
			
			elif (nroLayers == 3):
				print 'nroLayers: ' + str(nroLayers)
				imgModR = encodeIMG(arrayR, binData[:capacity])
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity])
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity])
				
				imgModA = arrayA
				
			elif (nroLayers == 2):
				print 'nroLayers: ' + str(nroLayers)
				imgModR = encodeIMG(arrayR, binData[:capacity])
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity])
				imgModB = arrayB
				imgModA = arrayA
				
				
			elif (nroLayers == 1):
				print 'nroLayers: ' + str(nroLayers)
				imgModR = encodeIMG(arrayR, binData)
				print np.ravel(imgModR)[:64]
				imgModG = arrayG
				imgModB = arrayB
				imgModA = arrayA
			
			R = Image.fromarray(imgModR)
			G = Image.fromarray(imgModG)
			B = Image.fromarray(imgModB)
			A = Image.fromarray(imgModA)
			imgMod = Image.merge('RGBA',(R,G,B,A))
			
	elif(type == 0): #mode RGB
		if(dataLen > capacity * 3):
			return -1
		else:
			nroLayers = math.ceil(dataLen/float(capacity))
			if (nroLayers == 3):
				imgModR = encodeIMG(arrayR, binData[:capacity])
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity])
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity])
				
			elif (nroLayers == 2):
				
				imgModR = encodeIMG(arrayR, binData[:capacity])
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity])
				
				imgModB = arrayB
				
			elif (nroLayers == 1):
				imgModR = encodeIMG(arrayR, binData)
				imgModG = arrayG
				imgModB = arrayB
			
			R = Image.fromarray(imgModR)
			G = Image.fromarray(imgModG)
			B = Image.fromarray(imgModB)
			imgMod = Image.merge('RGB',(R,G,B))
	
	
	imgMod.save("ImgModColor.png","PNG")
	
	# Decoding Part:
	message = ''
	
	print 'Hi Test'
	
	if(imgMod.mode == "RGBA"):
		R,G,B,A = imgMod.split()
		arrayR = np.asarray(R)
		print np.ravel(arrayR)[:64]

		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		arrayA = np.asarray(A)
		type = 1
	elif(imgMod.mode == "L"):
		arrayL = np.asarray(imgMod)
		type = 2
	else:
		imgMod = imgMod.convert("RGB")
		R,G,B = imgMod.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		type = 0
	
	
	if (type == 2):
		message =  decodeLSB(arrayL.copy())
	elif (type == 1):
		while(messageCode != 0):
			if (messageCode == 1):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayR.copy())
			elif (messageCode == 2):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayG.copy())
			elif (messageCode == 3):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayB.copy())
			elif (messageCode == 4):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayA.copy())
	elif (type == 0):
		while(messageCode != 0):
			if (messageCode == 1):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayR.copy())
			elif (messageCode == 2):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayG.copy())
			elif (messageCode == 3):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayB.copy())
			
			

	print message[:64]
	n = int('0b'+message,2)
	print binascii.unhexlify('%x' % n)
	
	
	
	imgMod.show()
	
	
if __name__ == "__main__":
	Main(sys.argv[1:])