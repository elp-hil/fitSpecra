import h5py
def read(file):
	return h5py.File(file)['save_data']
def readParameters(file):
	parameters = h5py.File(file)
	print("parameters:\n")
	print(parameters)
	return int(parameters['detect']['samples'][0,0]), int(parameters['samplingRate'][0,0]), int(parameters['pulse']['scans'][0,0])
