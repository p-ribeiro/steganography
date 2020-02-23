######################################################################


from numpy import empty,arange,exp,real,imag,pi
from numpy.fft import rfft,irfft


######################################################################
# 1D DCT Type-II

def dct(y):
    N = len(y)
    y2 = empty(2*N,float)
    y2[:N] = y[:]
    y2[N:] = y[::-1]

    c = rfft(y2)
    phi = exp(-1j*pi*arange(N)/(2*N))
    return real(phi*c[:N])


######################################################################
# 1D inverse DCT Type-II

def idct(a):
    N = len(a)
    c = empty(N+1,complex)

    phi = exp(1j*pi*arange(N)/(2*N))
    c[:N] = phi*a
    c[N] = 0.0
    return irfft(c)[:N]


######################################################################
# 2D DCT

def dct2(y):
    M = y.shape[0]
    N = y.shape[1]
    a = empty([M,N],float)
    b = empty([M,N],float)

    for i in range(M):
        a[i,:] = dct(y[i,:])
    for j in range(N):
        b[:,j] = dct(a[:,j])

    return b


######################################################################
# 2D inverse DCT

def idct2(b):
    M = b.shape[0]
    N = b.shape[1]
    a = empty([M,N],float)
    y = empty([M,N],float)

    for i in range(M):
        a[i,:] = idct(b[i,:])
    for j in range(N):
        y[:,j] = idct(a[:,j])

    return y






# Based on code on https://rosettacode.org/wiki/Zig-zag_matrix#Python
def zigzagIndices(n):
	
	indexorder = sorted(((x,y) for x in range(n) for y in range(n)), key = lambda (x,y): (x+y, -y if (x+y)%2 else y))
	
	return indexorder

def Main():
	import numpy as np
	import ia636 as ia
	from scipy.fftpack import dct, idct
	
	A = [[139, 144, 149, 153, 155, 155, 155, 155],
	     [144, 151, 153, 156, 159, 156, 156, 156],
		 [150, 155, 160, 163, 158, 156, 156, 156],
		 [159, 161, 162, 160, 160, 159, 159, 159],
		 [159, 160, 161, 162, 162, 155, 155, 155],
		 [161, 161, 161, 161, 160, 157, 157, 157],
		 [162, 162, 161, 163, 162, 157, 157, 157],
		 [162, 162, 161, 161, 163, 158, 158, 158]]

		 
	dctIa = ia.iadct(A).round()
	dctScipy = dct(A,type = 2,axis = -1,norm ='ortho').round()
	
	print 'dctIa'
	print dctIa.astype('int')
	d2 = dct2(np.asarray(A)).round().astype('int')
	print d2
	id2 = idct2(d2).round().astype('int')
	idctIa = ia.iaidct(dctIa).round().astype('int')
	print id2 == A
		 
		 
		 
if __name__ == '__main__':
	Main()