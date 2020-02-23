from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct
import ia636 as ia
import sys
from math import ceil, floor
import binascii


bitNroEncode = 0

matrixTest = []

quantizationTable = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
							  [12, 12, 14, 19, 26, 58, 60, 55],
							  [14, 13, 16, 24, 40, 57, 69, 56],
							  [14, 17, 22, 29, 51, 87, 80, 62],
							  [18, 22, 37, 56, 68, 109, 103, 77],
							  [24, 35, 55, 64, 81, 104, 113, 92],
							  [49, 64, 78, 87, 103, 121, 120, 101],
							  [72, 92, 95, 98, 112, 100, 103, 99]])

# Based on code on https://rosettacode.org/wiki/Zig-zag_matrix#Python
# Return indices on ZigZag reading of 2D array
def zigzagIndices(n):
	
	indexorder = sorted(((x,y) for x in range(n) for y in range(n)), key = lambda (x,y): (x+y, -y if (x+y)%2 else y))
	
	return indexorder

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
def encodeDCT(imgBlock, data):
	global bitNroEncode
	global matrixTest
	controlBlock = imgBlock.copy()
	
	indices = zigzagIndices(8)
	
	for lin,col in indices:
		if(len(data) > 0):
			bit = data[:1] #first element from data
			data = data[1:] #removing first element from data
			dataByte = imgBlock[lin][col].astype('int32')
			lastBit = bin(dataByte)[-1:]
			
			
			encodedByte = bin(dataByte)[:-1] + bit #+lastBit
			
			
			BackUp = imgBlock[lin][col]
			bitNroEncode = bitNroEncode + 1
			if(encodedByte[:1] == '-'):
				imgBlock[lin][col] = (-1)*int(encodedByte[1:],2)
				
			else:
				imgBlock[lin][col] = int(encodedByte,2)
				
				
				
	return imgBlock

	
#Funciona!!
def decodeDCT(img):
	message = ''
	cnt = 1
	bitNro = 0 
	
	global matrixTest
	global quantizationTable
	
	indices = zigzagIndices(8)
	
	for lin in xrange(0,img.shape[0]-1,8):
		for col in xrange(0,img.shape[1]-1,8):
			b = blocks8by8(img,lin, col)
			
			dctB = ia.iadct(b - 128).round()
			
			if(cnt == 1):
				print "Comparing DCT from coverImage with encodedBlock"
				print matrixTest
				print dctB
				print dctB == matrixTest
			
			for lin,col in indices:
				byte = dctB[lin][col]
				bit = bin(byte.astype('int32'))[-1:]
				
				#encodedByte = byte.astype('int32')
				
				message = message + bit
				bitNro = bitNro + 1
				if message[-16:] == "0010101000101010":
					print len(message)
					return message[:-16]
				
			cnt = cnt + 1
			
				
				
	return message	
	
	


	
def Main(argv):
	filename = sys.argv[1]
	img = Image.open(filename)
	data = "Try to encode me, I double dare you"
	#binData = ''.join(format(ord(x),'b') for x in data)
	data = data + "***" # end of message
	
	
	global matrixTest
	global quantizationTable
	
	binData = bin(int(binascii.hexlify(data), 16))[2:]
	print binData
	print len(binData)
	binDataBackUp = binData
	#decoding : 
	n = int('0b'+binData,2)
	print "decoded: " + binascii.unhexlify('%x' % n)
	
	
	#dct_coef = dct(img)
	img_array = np.asarray( img, dtype="int32" )
	img = img.convert("RGB")
	print img.size
	#data = img.getdata()
	
	#adds zero to the borders so the image can have a interger number of
	#blocks 8x8
	img2 = np.array(img)
	base2D = np.zeros_like(img2[:,:,0])
	
	nroBlocks = ceil(len(binData)/64.0)
	
	
	# For each 8x8 Block, a dct is made, information is added and idct is made so the image is mounted again
	for lin in xrange(0,img2.shape[0]-1,8):
		for col in xrange(0,img2.shape[1]-1,8):
			b = blocks8by8(img2,lin, col)
			if (nroBlocks > 0):
				print nroBlocks
				
			
				
					
				dctB = ia.iadct(b - 128).round()
				print "dctB"
				print dctB
				# dctB = dct(idct(dct(b - 128, norm='ortho'),norm='ortho'),norm='ortho').round()
					
				#quantizedDCT = (dctB/quantizationTable).round()
				# print quantizedDCT.copy()
				encodedBlock = encodeLSB(dctB.copy(),binData[:64])
				binData = binData[64:]
				
				if(nroBlocks == 5):
					matrixTest = encodedBlock.copy()
				#encodedBlock = encodedBlock * quantizationTable
				idctB = (ia.iaidct(encodedBlock)+128).round()
				print "idctB"
				print idctB
				# idctB = (idct(encodedBlock, norm='ortho') + 128).round()#-- IDCT
				
				nroBlocks = nroBlocks - 1
				
				
			else:
				idctB = b
				
			imgMod = insertBlock(idctB,base2D,lin,col)

	
	print imgMod.shape
	

	
	message =  decodeLSB(imgMod.copy())
	
	if(message[:64] == binDataBackUp[:64]):
		print "Hora de festejar pt. 1"
	else:
		print "Not there yet"
	
	print message[:64]
	n = int('0b'+message,2)
	#print binascii.unhexlify('%x' % n)
	
	
	imgMod = Image.fromarray(imgMod, 'L')
	
	
	
	imgMod.show()
	
	
	
	
	
if __name__ == "__main__":
	Main(sys.argv[1:])