import scipy.io as sio 
import os
import numpy as np
import matFile
import datFile
def read(file, override):
	filename, fileExtension = os.path.splitext(file)
	if override == 0:
		if fileExtension == '.mat':
			dataRead = matFile.read(file)
			timePoints = dataRead[0,:]
			data = dataRead[1:dataRead[:,0].size-1]
			parameters = matFile.readParameters(filename+'parameter.mat')
		elif fileExtension == '.dat':
			dataRead =  datFile.read(file)
		else:
			print('File format not recognized, please override to a specific format')
	elif override == 1:
		dataRead = matFile.read(file)
	elif override == 2:
		dataRead = datFile(file)
	else:
		print("Please choose valid override parameter:\n 1: .mat file\n 2: .dat file")		
	return parameters, data
def sumIt(data):
	print ('summing\n')
	return np.sum(data)	

