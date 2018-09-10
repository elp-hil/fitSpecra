import h5py
def read(file):
	return h5py.File(file)['save_data']
def readParameters(file):
	parameters = h5py.File(file)
	return int(parameters['detect']['samples'][0,0]), int(parameters['samplingRate'][0,0])
