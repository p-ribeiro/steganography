import numpy as np

A = (np.random.rand(1000)*100).round().astype('int')

B = ''.join([format(x,'09b') for x in A]) 

print len(B) % 9

C = []

while len(B)>0:
	C.append(B[:9])
	B = B[9:]

	

D = [int(n,2) for n in C]

print D == A
