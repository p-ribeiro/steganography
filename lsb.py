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


# ---------------------------------------- Global variables
bitNroEncode = 0
nroBlocks = 0
messageCode = 1
dctDecoded = []
dctEncoded = []


## -------------------------------------- Enums
class ImageType(Enum):
    RGB = 0
    RGBA = 1
    L = 2  # 8-Bit B&W


def blocks8by8(img, xOrigin, yOrigin):

    block = np.zeros((8, 8))

    for y in range(yOrigin, yOrigin + 8):
        for x in range(xOrigin, xOrigin + 8):
            if img.ndim > 2:
                block[x - xOrigin][y-yOrigin] = img[x][y][0]
            else:
                block[x - xOrigin][y-yOrigin] = img[x][y]
    return block


def insertBlock(block, imgMod, yOrigin, xOrigin):
    for lin in range(8):
        for col in range(8):
            imgMod[lin + yOrigin][col + xOrigin] = block[lin][col]

    return imgMod


def encodeLSB(imgBlock, data):
    '''Insert the 64 bit part of data into the 8x8 image block
    
    Parameters
    ----------
    imgBlock: 8x8 array
        The 64 byte block of the cover image
    
    data: binary
        The 64 bits part of data to be encoded in this block
    
    '''
    global bitNroEncode

    for lin in range(8):
        for col in range(8):
            if(len(data) > 0):
                bit = data[:1]  # first element from data
                data = data[1:]  # removing first element from data
                dataByte = imgBlock[lin][col].astype('int32')
                encodedByte = bin(dataByte)[:-1] + bit
                bitNroEncode = bitNroEncode + 1
                if(encodedByte[:1] == '-'):
                    imgBlock[lin][col] = (-1)*int(encodedByte[1:], 2)
                else:
                    imgBlock[lin][col] = int(encodedByte, 2)
    return imgBlock

def decodeLSB(img, is_dct):
    message = ''
    bitNro = 0

    h = img.shape[0] % 8
    w = img.shape[1] % 8

    global messageCode
    global dctDecoded

    for lin in range(0, img.shape[0]-h,8):
        for col in range(0, img.shape[1]-w,8):

            b = blocks8by8(img, lin, col)

            if(is_dct):
                b = ia.iadct(b - 128).round().astype(int)
                if (bitNro == 0):
                    dctDecoded = b


            for idx, byte in np.ndenumerate(b):

                bit = bin(byte.astype('int'))[-1:]

                message = message + bit
                bitNro = bitNro + 1
                if message[-16:] == bin(0xFFAA)[2:]:
                    messageCode = 0
                    return message[:-16]


    return message


def encodeIMG(img, binData, is_dct):
    '''For each 8x8 Block, information is added and the image is mounted again
    Parameters
    ----------
    img: array
        It's the cover image in array format
    
    binData: binary
        It is the message to be encoded in binary format
    
    is_dct: Boolean
        True if the method used is Discrete Cosine Transform (DCT)
    '''
    h = img.shape[0] % 8
    w = img.shape[1] % 8
    base2D = np.zeros_like(img)
    global nroBlocks
    global dctEncoded

    nroInit = nroBlocks
    for lin in range(0, img.shape[0]-h,8):
        for col in range(0, img.shape[1]-w,8):
            b = blocks8by8(img, lin, col)

            if (nroBlocks > 0):
                if(is_dct):
                    b = ia.iadct(b - 128).round().astype(int)

                encodedBlock = encodeLSB(b.copy(), binData[:64])
                binData = binData[64:]

                if(is_dct):
                    if(nroBlocks == nroInit):
                        dctEncoded = b
                    b = ((ia.iaidct(b) + 128).round()).astype(int)
                else:
                    b = encodedBlock

                nroBlocks = nroBlocks - 1

            imgMod = insertBlock(b, base2D,lin,col)
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
            True if the method used is Discrete Cosine Transform (DCT)
    is_img: Boolean
            True if the message to be encoded is an image
    '''
    imgType = None

    global messageCode
    global nroBlocks

    if is_img:
        binData = ''.join([format(x, '09b') for x in data]) + bin(0xFFAA)[2:] ##Sinal de fim da mensagem
    else:
        binData = bin(int(binascii.hexlify(data), 16))[2:] + bin(0xFFAA)[2:]  # Sinal de fim da mensagem

    dataLen = len(binData)
    # binDataBackUp = binData

    if(img.mode == "RGBA"):
        R, G,B,A = img.split()
        arrayR = np.asarray(R)
        arrayG = np.asarray(G)
        arrayB = np.asarray(B)
        arrayA = np.asarray(A)
        imgType = ImageType.RGBA
    elif(img.mode == "L"):
        arrayL = np.asarray(img)
        imgType = ImageType.L
    else:
        img = img.convert("RGB")
        R, G,B = img.split()
        arrayR = np.asarray(R)
        arrayG = np.asarray(G)
        arrayB = np.asarray(B)
        imgType = ImageType.RGB
    print(img.size)

    nroBlocks = math.ceil(dataLen/64.0)
    imgMod = []

    w = img.size[0]
    h = img.size[1]

    capacity = (w - w %8)*(h - h %8)
    print('Tamanho Total do dado a ser inserido: ' + str(dataLen)+'\n')
    print ('Quantidade de bits que podem ser modificados em uma camada da imagem: ' + str(capacity) + '\n')

    if(imgType == ImageType.L):
        if(dataLen > capacity):
            print('Imagem não possui tamanho suficiente para esconder informação \n')
            return -1
        else:
            imgMod = encodeIMG(arrayL, binData, is_dct)
            imgMod = Image.fromarray(imgMod, 'L')
            return imgMod

    elif(imgType == ImageType.RGBA):  # mode RGBA
        if(dataLen > capacity * 4):
            print('Imagem não possui tamanho suficiente para esconder informação \n')
            return -1
        else:
            nroLayers = math.ceil(dataLen/float(capacity))
            print('Número de camadas necessárias para armazenar o dado: ' + str(nroLayers)+'\n')

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
            imgMod = Image.merge('RGBA', (R,G,B,A))
            #imgMod = np.stack((imgModR, imgModG, imgModB, imgModA))
            return imgMod

    elif(imgType == ImageType.RGB):  # mode RGB
        if(dataLen > capacity * 3):
            print('Imagem não possui tamanho suficiente para esconder informação \n')
            return -1
        else:
            nroLayers = math.ceil(dataLen/float(capacity))
            print('Número de camadas necessárias para armazenar o dado: ' + str(nroLayers)+'\n')
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
            imgMod = Image.merge('RGB', (R,G,B))
            #imgMod = np.stack((imgModR,imgModG,imgModB))
            return imgMod


def RetreiveLSB(img, is_dct, is_img):
    '''Retreive the data from the cover image
    Parameters
    ----------
    img: PIL
            It's the image in which a message is hidden
    is_dct:
            True if the method used is Discrete Cosine Transform (DCT)
    is_img:
            True if the message to be encoded is an image
    '''
    global messageCode
    messageCode = 1

    message = ''
    if(img.mode == "RGBA"):
        R, G,B,A = img.split()
        arrayR = np.asarray(R)
        arrayG = np.asarray(G)
        arrayB = np.asarray(B)
        arrayA = np.asarray(A)
        imgType = ImageType.RGBA
    elif(img.mode == "L"):
        arrayL = np.asarray(img)
        imgType = ImageType.L
    else:
        img = img.convert("RGB")
        R, G,B = img.split()
        arrayR = np.asarray(R)
        arrayG = np.asarray(G)
        arrayB = np.asarray(B)
        imgType = ImageType.RGB

    if (imgType == ImageType.L):
        message = decodeLSB(arrayL.copy(), is_dct)
    elif (imgType == ImageType.RGBA):
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
    elif (imgType == ImageType.RGB):
        while(messageCode != 0):
            if (messageCode == 1):
                print("Camada R")
                messageCode = messageCode + 1
                message = message + decodeLSB(arrayR.copy(), is_dct)
            elif (messageCode == 2):
                print("Camada G")
                messageCode = messageCode + 1
                message = message + decodeLSB(arrayG.copy(), is_dct)
            elif (messageCode == 3):
                messageCode = messageCode + 1
                message = message + decodeLSB(arrayB.copy(), is_dct)

    print("Decoding message")
    if is_img:
        msg = []
        while len(message) > 0:
            msg.append(message[:9])
            message = message[9:]
        imgArr = [int(n, 2) for n in msg]
        return imgArr
    elif is_dct:
        n = int('0b'+message, 2)
    else:
        n = int('0b'+message, 2)
        return binascii.unhexlify('%x' % n)
