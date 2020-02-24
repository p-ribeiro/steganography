# coding=utf8

from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct
import ia636 as ia
import sys
import math
import binascii
import hashlib
import io


bitNroEncode = 0
nroBlocks = 0
messageCode = 1
dctDecoded = []
dctEncoded = []
test = ''

def getImageMd5Hash(img):
	'''Takes the md5 of a image open with PIL (only for png, for now) 
	
	Parameters
	----------
	img : PIL
		Image file open with PIL
	
	'''
	m = hashlib.md5()
	with io.BytesIO() as memf:
		img.save(memf, 'PNG')
		data = memf.getvalue()
		m.update(data)
	
	return m.hexdigest()


def array2pil(arr):

    nd = len(arr.shape)
    x = arr.astype('B')
    if nd == 2:
        d, h, w = (1,) + arr.shape
        mode = 'L'
    elif nd == 3:
        if arr.dtype.char == '?':
            raise ("Binary array cannot be RGB")
        d, h, w = arr.shape
        if   d == 1: mode = 'L'
        elif d == 3: mode = 'RGB'
        elif d == 4: mode = 'RGBA'
        else:
            raise ("Array first dimension must be 1, 3 or 4 (%d)" % d)
    else:
        raise ("Array must have 2 or 3 dimensions (%d)" % nd)
    if d > 1:
        x = np.swapaxes(np.swapaxes(x, 1, 2), 0, 2)
    pil = Image.frombytes(mode, (w,h), x.tobytes())
    if arr.dtype.char == '?':
        pil = pil.point(lambda i: i>0, '1')
    return pil


def pil2array(pil):
	
	w, h = pil.size
	binary = 0
	if pil.mode == '1':
		binary = 1
		pil = pil.convert('L')
	if pil.mode == 'L':
		d = 1 ; shape = (h,w)
	elif pil.mode == 'P':
		if 0:   # len(pil.palette.data) == 2*len(pil.palette.rawmode):
			binary = 1
			pil = pil.convert('L')
			d = 1 ; shape = (h,w)
		else:
			pil = pil.convert('RGB')
			d = 3 ; shape = (h,w,d)
	elif pil.mode in ('RGB','YCbCr'):
		d = 3 ; shape = (h,w,d)
	elif pil.mode in ('RGBA','CMYK'):
		d = 4 ; shape = (h,w,d)
	else:
		raise ("Invalid or unimplemented PIL image mode '%s'" % pil.mode)
	arr = np.reshape(np.frombuffer(pil.tobytes(), 'B', w*h*d), shape)
	if d > 1:
		arr = np.swapaxes(np.swapaxes(arr, 0, 2), 1, 2)
	if binary:
		arr = arr.astype('?')
	return arr

  
def img2arr(image):
	''' Transforms an image to an array '''
	g = image.flatten()   
	if (len(image.shape) >= 3):
		a=np.array([image.shape[0],image.shape[1],image.shape[2]])
		arr = np.concatenate((a,g),axis=0)
	else:
		a=np.array([0,image.shape[0],image.shape[1]])
		arr = np.concatenate((a,g),axis=0)
		
	return arr
	
# reshape da imagem
def arr2img(arr):
	
	if (arr[0]==0):
		img=np.reshape(arr[3:],(arr[1],arr[2]))
	else:
		img=np.reshape(arr[3:],(arr[0],arr[1],arr[2]))
	return(img)
	
# Based on code on https://rosettacode.org/wiki/Zig-zag_matrix#Python
# Return indices on ZigZag reading of 2D array
# def zigzagIndices(n):
	
# 	indexorder = sorted(((x,y) for x in range(n) for y in range(n)), key = lambda x_y: (x_y[0] + x_y[1], -x_y[1] if (x_y[0] +x_y[1])%2 else x_y[1]))


def blocks8by8(img,xOrigin, yOrigin):
	
	block = np.zeros((8,8))
	
	for y in range(yOrigin,yOrigin + 8):
		for x in range(xOrigin, xOrigin + 8):
			if img.ndim > 2:
				block[x - xOrigin][y-yOrigin] = img[x][y][0]
			else:
				block[x - xOrigin][y-yOrigin] = img[x][y]
	return block
		
def insertBlock(block,imgMod, yOrigin, xOrigin):
	for lin in range(8):
		for col in range(8):
			imgMod[lin + yOrigin][col + xOrigin] = block[lin][col]
			
	return imgMod       
	  
def encodeLSB(imgBlock, data):

	global bitNroEncode
	controlBlock = imgBlock.copy()
	
	for lin in range(8):
		for col in range(8):
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


def decodeLSB(img, is_dct):
	message = ''
	cnt = 1
	bitNro = 0 
	
	h = img.shape[0] % 8
	w = img.shape[1] % 8
	
	global messageCode
	global dctDecoded
	
	for lin in range(0,img.shape[0]-h,8):
		for col in range(0,img.shape[1]-w,8):
			
			b = blocks8by8(img,lin, col)
			
			if(is_dct):
				b = ia.iadct(b - 128).round().astype(int)
				if (bitNro == 0):
					dctDecoded = b
				
			
			for idx,byte in np.ndenumerate(b):
			
				bit = bin(byte.astype('int'))[-1:]
				
				# encodedByte = byte.astype('int32')
				
				message = message + bit
				bitNro = bitNro + 1
				if message[-16:] == bin(0xFFAA)[2:]:
					messageCode = 0
					return message[:-16]
				
			cnt = cnt + 1
				
				
	return message  
	
	
def encodeIMG(img, binData, is_dct):
	# For each 8x8 Block, information is added and the image is mounted again
	h = img.shape[0] % 8
	w = img.shape[1] % 8
	base2D = np.zeros_like(img)
	global nroBlocks
	global dctEncoded
	
	nroInit = nroBlocks
	for lin in range(0,img.shape[0]-h,8):
		for col in range(0,img.shape[1]-w,8):
			b = blocks8by8(img,lin, col)
							
			if (nroBlocks > 0):
				if(is_dct):
					b = ia.iadct(b - 128).round().astype(int)
					
				encodedBlock = encodeLSB(b.copy(),binData[:64])
				binData = binData[64:]
				
				if(is_dct):
					if(nroBlocks == nroInit):
						dctEncoded = b
					b = ((ia.iaidct(b) + 128).round()).astype(int)
				else:
					b = encodedBlock
				
				nroBlocks = nroBlocks - 1
				
			imgMod = insertBlock(b,base2D,lin,col)
	return imgMod
	
def InsertLSB(img, data, is_dct, is_img):
	'''Insert the message to be hidden into the cover image using the Least Significant Bit (LSB) method 
	
	Parameters
	----------
	img: array
		Is the cover image in array format
	
	data: array
		Is the message (text or image) to be hidden in array format

	is_dct: Boolean
		If the method used Discrete Cosine Transform (DCT)
	
	is_img: Boolean
		If it message is an image or an text
	
	'''

	# imgType == 0 -> the image is in RGB
	# imgType == 1 -> the image is in RGBA
	# imgType == 2 -> the image is in 8-bit B&W
	imgType = None
	
	global messageCode
	global nroBlocks
	
	if is_img:
		binData = ''.join([format(x,'09b') for x in data]) + bin(0xFFAA)[2:] ##Sinal de fim da mensagem
	else:   
		binData = bin(int(binascii.hexlify(data), 16))[2:] + bin(0xFFAA)[2:] ##Sinal de fim da mensagem
   
	dataLen =  len(binData)
	# binDataBackUp = binData
	
	
	if(img.mode == "RGBA"):
		R,G,B,A = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		arrayA = np.asarray(A)
		imgType = 1
	elif(img.mode == "L"):
		arrayL = np.asarray(img)
		imgType = 2
	else:
		img = img.convert("RGB")
		R,G,B = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		imgType = 0
	print(img.size)
	

	nroBlocks = math.ceil(dataLen/64.0)
	imgMod = []
	
	# if type == 2:
		# h = img.shape[0]
		# w = img.shape[1]
	# else:
		# h = img.shape[1]
		# w = img.shape[2]
	w = img.size[0]
	h = img.size[1]
	
	
	capacity = (w - w%8)*(h - h%8)
	print ('Tamanho Total do dado a ser inserido: ' + str(dataLen)+'\n')
	print ('Quantidade de bits que podem ser modificados em uma camada da imagem: ' + str(capacity) +'\n')
	
	if(imgType == 2): #Mode L
		if(dataLen > capacity):
			print ('Imagem não possui tamanho suficiente para esconder informação \n')
			return -1
		else:
			imgMod = encodeIMG(arrayL, binData, is_dct)
			imgMod = Image.fromarray(imgMod, 'L')
			return imgMod
			
	elif(imgType == 1): #mode RGBA
		if(dataLen > capacity * 4):
			print ('Imagem não possui tamanho suficiente para esconder informação \n')
			return -1
		else:
			nroLayers = math.ceil(dataLen/float(capacity))
			print ('Número de camadas necessárias para armazenar o dado: ' + str(nroLayers)+'\n')
			
			if(nroLayers == 4):
				imgModR = encodeIMG(arrayR, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModA = encodeIMG(arrayA, binData[:capacity], is_dct)
			
			
			elif (nroLayers == 3):
				imgModR = encodeIMG(arrayR, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity], is_dct)
				
				imgModA = arrayA
				
			elif (nroLayers == 2):
				imgModR = encodeIMG(arrayR, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity], is_dct)
				imgModB = arrayB
				imgModA = arrayA
				
				
			elif (nroLayers == 1):
				imgModR = encodeIMG(arrayR, binData, is_dct)
				imgModG = arrayG
				imgModB = arrayB
				imgModA = arrayA
			
			R = Image.fromarray(imgModR)
			G = Image.fromarray(imgModG)
			B = Image.fromarray(imgModB)
			A = Image.fromarray(imgModA)
			imgMod = Image.merge('RGBA',(R,G,B,A))
			#imgMod = np.stack((imgModR, imgModG, imgModB, imgModA))
			return imgMod
			
	elif(imgType == 0): #mode RGB
		if(dataLen > capacity * 3):
			print ('Imagem não possui tamanho suficiente para esconder informação \n')
			return -1
		else:
			nroLayers = math.ceil(dataLen/float(capacity))
			print ('Número de camadas necessárias para armazenar o dado: ' + str(nroLayers)+'\n')
			if (nroLayers == 3):
				imgModR = encodeIMG(arrayR, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModB = encodeIMG(arrayB, binData[:capacity], is_dct)
			elif (nroLayers == 2):
				
				imgModR = encodeIMG(arrayR, binData[:capacity], is_dct)
				binData = binData[capacity:]
			
				imgModG = encodeIMG(arrayG, binData[:capacity], is_dct)
				
				imgModB = arrayB
				
			elif (nroLayers == 1):
				imgModR = encodeIMG(arrayR, binData, is_dct)
				imgModG = arrayG
				imgModB = arrayB
			
			R = Image.fromarray(imgModR)
			G = Image.fromarray(imgModG)
			B = Image.fromarray(imgModB)
			imgMod = Image.merge('RGB',(R,G,B))
			#imgMod = np.stack((imgModR,imgModG,imgModB))
			return imgMod
	

def RetreiveLSB(img, is_dct, is_img):
	'''Retreive the data from the cover image
	
	Parameters
	----------
	img: PIL
		It's the image in which a message is hidden

	is_dct:
		If it uses the Discrete Cosine Transform
	
	is_img:
		If the message hidden is an image or a text
	
	'''
	global messageCode
	messageCode = 1
	
	message = ''
	
	# if(img.shape[0] == 3):
		# arrayR, arrayG, arrayB = img
		# imgType = 0
	# elif(img.shape[0] == 4):
		# arrayR, arrayG, arrayB, arrayA = img
		# imgType = 1
	# else:
		# arrayL = img
		# imgType = 2

	if(img.mode == "RGBA"):
		R,G,B,A = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		arrayA = np.asarray(A)
		imgType = 1
	elif(img.mode == "L"):
		arrayL = np.asarray(img)
		imgType = 2
	else:
		img = img.convert("RGB")
		R,G,B = img.split()
		arrayR = np.asarray(R)
		arrayG = np.asarray(G)
		arrayB = np.asarray(B)
		imgType = 0
	
	
	if (imgType == 2):
		message =  decodeLSB(arrayL.copy(), is_dct)
	elif (imgType == 1):
		while(messageCode != 0):
			if (messageCode == 1):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayR.copy(), is_dct)
			elif (messageCode == 2):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayG.copy(), is_dct)
			elif (messageCode == 3):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayB.copy(), is_dct)
			elif (messageCode == 4):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayA.copy(), is_dct)
	elif (imgType == 0):
		while(messageCode != 0):
			if (messageCode == 1):
				print ("Camada R")
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayR.copy(), is_dct)
			elif (messageCode == 2):
				print ("Camada G")
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayG.copy(), is_dct)
			elif (messageCode == 3):
				messageCode = messageCode + 1
				message = message + decodeLSB(arrayB.copy(), is_dct)
	
	print ("Decoding message")
	if is_img:
		msg = []
		while len(message) > 0:
			# print len(message)
			msg.append(message[:9])
			message = message[9:]
		imgArr = [int(n,2) for n in msg]
		return imgArr
	elif is_dct:
		#return message
		n = int('0b'+message,2)
		#return binascii.unhexlify('%x' % n)
	else:
		n = int('0b'+message,2)
		return binascii.unhexlify('%x' % n)
		
# def psnr(dataset1, dataset2, maximumDataValue):
   
# 	# Make sure that the provided data sets are numpy ndarrays, if not
# 	# convert them and flatten te data sets for analysis
# 	if type(dataset1).__module__ != np.__name__:
# 	  d1 = np.asarray(dataset1).flatten()
# 	else:
# 	  d1 = dataset1.flatten()

# 	if type(dataset2).__module__ != np.__name__:
# 	  d2 = np.asarray(dataset2).flatten()
# 	else:
# 	  d2 = dataset2.flatten()

# 	# Make sure that the provided data sets are the same size
# 	if d1.size != d2.size:
# 	  raise ValueError('Provided datasets must have the same size/shape')

# 	# Check if the provided data sets are identical, and if so, return an
# 	# infinite peak-signal-to-noise ratio
# 	if np.array_equal(d1, d2):
# 	  return float('inf')

# 	error = d1.astype(np.float64)-d2.astype(np.float64)

# 	# Compute the mean-squared error
# 	meanSquaredError = np.sum(error**2) / error.size

# 	# Return the peak-signal-to-noise ratio
# 	return 10.0 * np.log10(maximumDataValue**2 / meanSquaredError)
   
# def MSE(dataset1, dataset2):

# 	# Make sure that the provided data sets are numpy ndarrays, if not
# 	# convert them and flatten te data sets for analysis
# 	if type(dataset1).__module__ != np.__name__:
# 	  d1 = np.asarray(dataset1).flatten()
# 	else:
# 	  d1 = dataset1.flatten()

# 	if type(dataset2).__module__ != np.__name__:
# 	  d2 = np.asarray(dataset2).flatten()
# 	else:
# 	  d2 = dataset2.flatten()

# 	# Make sure that the provided data sets are the same size
# 	if d1.size != d2.size:
# 	  raise ValueError('Provided datasets must have the same size/shape')

# 	error = d1.astype(np.float64)-d2.astype(np.float64)

# 	# Return the mean-squared error
# 	meanSquaredError = np.sum(error**2) / error.size
# 	return meanSquaredError
   
# def MAE(dataset1, dataset2):

# 	# Make sure that the provided data sets are numpy ndarrays, if not
# 	# convert them and flatten te data sets for analysis
# 	if type(dataset1).__module__ != np.__name__:
# 	  d1 = np.asarray(dataset1).flatten()
# 	else:
# 	  d1 = dataset1.flatten()

# 	if type(dataset2).__module__ != np.__name__:
# 	  d2 = np.asarray(dataset2).flatten()
# 	else:
# 	  d2 = dataset2.flatten()

# 	# Make sure that the provided data sets are the same size
# 	if d1.size != d2.size:
# 	  raise ValueError('Provided datasets must have the same size/shape')

# 	error = d1.astype(np.float64)-d2.astype(np.float64)

# 	# Return the mean absolute error
# 	meanAbsoluteError = np.sum(abs(error)) / error.size
# 	return meanAbsoluteError
	
	
def Main(filename):
	
	is_img = False
	imageFolder = "Imagens/"
	textFolder = "Textos/"

	if is_img:
		
		hiddenImage = Image.open(imageFolder + 'lilMona.jpg')
		# get the md5 hash of the image to be hidden
		hiddenImageHash = getImageMd5Hash(hiddenImage)
		smallImage = pil2array(hiddenImage)
		message = img2arr(smallImage)
	else:
		message = open(textFolder+'alice30.txt','rb').read()
		messageHash = hashlib.md5(message).hexdigest()
	


	# open cover image and transform it to an array
	coverImage = Image.open(imageFolder + filename)
	
	
	## ------------------- Hidding image or text -------------------------- ##
	print ("Imagem do tipo : %s\n" % coverImage.mode)
	print ("Entrando no InsertLSB")
	stegoImg = InsertLSB(coverImage, message, False, is_img)
	if stegoImg == -1:
		return
	## ------------------ Retreiving the image or text ------------------- ##
	print ("Entrando em RetreiveLSB")
	retInfo = RetreiveLSB(stegoImg, False,is_img)
	stegoImg.save("Stego1.png","PNG")
	
	if is_img:
		retInfo = arr2img(retInfo)
		retInfo = array2pil(np.asarray(retInfo))
		
		## ------------------ Comparing images ------------------------------- ##
		retImgHash = getImageMd5Hash(retInfo)
		if(retImgHash == hiddenImageHash):
			print("The images are equal")
		else:
			print("Hash of original image: " + messageHash)
			print("\nHash of retrived image: " + retImgHash)
		## ---------------- Saving and showing the results ------------------ ##
		retInfo.save("RetImg.png","PNG")
		retInfo.show()
	else:
		retHash = hashlib.md5(retInfo).hexdigest()
		retText = open("RetTxt.txt",'wb')
		retText.write(retInfo)
		retText.close()

	if retHash == messageHash:
		print("The text retreived is the same")
	else:
		print("Hash of original message: " + messageHash)
		print("\nHash of retrived message: " + retHash)

	stegoImg.show()
	
	
	
		

if __name__ == "__main__":
	# Image.open("Imagens/testColor.png")
	Main("medium.png")