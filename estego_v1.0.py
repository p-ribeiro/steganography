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
from enum import Enum
import lsb


## -------------------------------------- Functions

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
	stegoImg = lsb.InsertLSB(coverImage, message, False, is_img)
	if stegoImg == -1:
		return
	## ------------------ Retreiving the image or text ------------------- ##
	print ("Entrando em RetreiveLSB")
	retInfo = lsb.RetreiveLSB(stegoImg, False,is_img)
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