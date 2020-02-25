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