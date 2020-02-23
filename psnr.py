import ia636 as ia
import numpy
from PIL import Image

def psnr(dataset1, dataset2, maximumDataValue, ignore=None):
   
	# Make sure that the provided data sets are numpy ndarrays, if not
	# convert them and flatten te data sets for analysis
	if type(dataset1).__module__ != numpy.__name__:
	  d1 = numpy.asarray(dataset1).flatten()
	else:
	  d1 = dataset1.flatten()

	if type(dataset2).__module__ != numpy.__name__:
	  d2 = numpy.asarray(dataset2).flatten()
	else:
	  d2 = dataset2.flatten()

	# Make sure that the provided data sets are the same size
	if d1.size != d2.size:
	  raise ValueError('Provided datasets must have the same size/shape')

	# Check if the provided data sets are identical, and if so, return an
	# infinite peak-signal-to-noise ratio
	if numpy.array_equal(d1, d2):
	  return float('inf')

	# If specified, remove the values to ignore from the analysis and compute
	# the element-wise difference between the data sets
	if ignore is not None:
	  index = numpy.intersect1d(numpy.where(d1 != ignore)[0], 
							numpy.where(d2 != ignore)[0])
	  error = d1[index].astype(numpy.float64) - d2[index].astype(numpy.float64)
	else:
	  error = d1.astype(numpy.float64)-d2.astype(numpy.float64)

	# Compute the mean-squared error
	meanSquaredError = numpy.sum(error**2) / error.size

	# Return the peak-signal-to-noise ratio
	return 10.0 * numpy.log10(maximumDataValue**2 / meanSquaredError)
   
def MSE(dataset1, dataset2, ignore=None):

	# Make sure that the provided data sets are numpy ndarrays, if not
	# convert them and flatten te data sets for analysis
	if type(dataset1).__module__ != numpy.__name__:
	  d1 = numpy.asarray(dataset1).flatten()
	else:
	  d1 = dataset1.flatten()

	if type(dataset2).__module__ != numpy.__name__:
	  d2 = numpy.asarray(dataset2).flatten()
	else:
	  d2 = dataset2.flatten()

	# Make sure that the provided data sets are the same size
	if d1.size != d2.size:
	  raise ValueError('Provided datasets must have the same size/shape')

	# Check if the provided data sets are identical, and if so, return an
	# infinite peak-signal-to-noise ratio
	#if numpy.array_equal(d1, d2):
	#   return float(0)

	error = d1.astype(numpy.float64)-d2.astype(numpy.float64)

	# Return the mean-squared error
	meanSquaredError = numpy.sum(error**2) / error.size
	return meanSquaredError
   
def MAE(dataset1, dataset2, ignore=None):

	# Make sure that the provided data sets are numpy ndarrays, if not
	# convert them and flatten te data sets for analysis
	if type(dataset1).__module__ != numpy.__name__:
	  d1 = numpy.asarray(dataset1).flatten()
	else:
	  d1 = dataset1.flatten()

	if type(dataset2).__module__ != numpy.__name__:
	  d2 = numpy.asarray(dataset2).flatten()
	else:
	  d2 = dataset2.flatten()

	# Make sure that the provided data sets are the same size
	if d1.size != d2.size:
	  raise ValueError('Provided datasets must have the same size/shape')

	# Check if the provided data sets are identical, and if so, return an
	# infinite peak-signal-to-noise ratio
	# #if numpy.array_equal(d1, d2):
	#   return float('inf')

	error = d1.astype(numpy.float64)-d2.astype(numpy.float64)

	# Return the mean absolute error
	meanAbsoluteError = numpy.sum(abs(error)) / error.size
	return meanAbsoluteError


imgOriginal = Image.open('huge.png')
imgOriginal = numpy.asarray(imgOriginal)

imgMod = Image.open('stego1.png')
imgMod = numpy.asarray(imgMod)
	
print psnr(imgOriginal,imgMod,255)
print MSE(imgOriginal,imgMod)
print MAE(imgOriginal,imgMod)
