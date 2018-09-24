import os
import matFile
import datFile
import numpy as np
import math
import cmath
import pdb
from scipy.optimize import curve_fit
class data:
	def __init__(self, path):
		self.overrideType = 0
		self.fullPath = path

		self.data = np.array([])
		self.summedData = np.array([])
		self.fftData = np.array([])
		self.summedFftData = np.array([])

		self.frequencies = []
		self.timePoints = []
		self.samples = 0
		self.samplingRate = 0
		self.fitParameters = np.array([])
		self.summedFitParameters = np.array([])
		self.phase = np.array([]) #-2*cmath.pi
		self.summedPhase = 0
		self.function = 0
		self.numberOfParameters = np.array((3,3))
		self.nScans = 0
	def setType(self, dataType):
		self.overrideType = dataType
	def read(self):
		dataType = 0
		if self.overrideType != 0:
			dataType = self.overrideType
		else:
			filename, fileExtension = os.path.splitext(self.fullPath)
			if  ".mat" in fileExtension:
				dataType = 1
			elif  ".dat"== fileExtension:
				dataType = 2
			else:
				print('File format not recognized, please override to a specific format\n 1: .mat file\n 2: .dat file')
		if dataType == 1:
			tempData = matFile.read(self.fullPath)
			self.timePoints = tempData[0,:]
			self.data = tempData[1:tempData[:,0].size]
			self.samples, self.samplingRate, self.nScans = matFile.readParameters(filename+'parameter.mat')
		elif dataType == 2:
			self.data = datFile(self.fullPath)
		else:
			print("Please choose valid override parameter:\n 1: .mat file\n 2: .dat file")
		self.timepoints = np.linspace(0,False, self.samples)
		self.phase = np.zeros(self.data[:,0].size)
		self.fitParameters = np.zeros((self.nScans, self.numberOfParameters[self.function]))
		self.summedFitParameters = np.zeros((1,self.numberOfParameters[self.function]))
	def fft(self, omitSamples, sumScans = 0, zeroFill = 0):
		nextPowerOfTwo = int(math.pow(2,math.ceil(math.log((self.samples-omitSamples))/math.log(2.0))))
		print(nextPowerOfTwo)
		self.frequencies = np.linspace(0, self.samplingRate/2, nextPowerOfTwo*(zeroFill +1)/2)#(self.samples-omitSamples)/2)
		#np.pad(self.frequencies, (0,int(nextPowerOfTwo - (self.samples - omitSamples)/2) + zeroFill * int( (self.samples-omitSamples) /2)), 'constant', constant_values = 0)
		if sumScans:
			self.summedFftData = np.array([])
			if self.summedData.size == 0:
				self.sum()
			tmpData = np.pad(self.summedData[omitSamples:], (0,nextPowerOfTwo - (self.samples - omitSamples) + zeroFill * nextPowerOfTwo), 'constant', constant_values = 0)
			self.summedFftData =  np.fft.fftshift(np.fft.fft(tmpData))
			print(self.summedFftData)
		else:
			self.fftData = np.empty([0, int(nextPowerOfTwo *
			    (zeroFill+1))], dtype=float)
			self.phase[0] = -cmath.pi/8
			for i in range(0, self.data[:,0].size):
				tmpData = np.pad(self.data[i,omitSamples:], (0,nextPowerOfTwo - (self.samples - omitSamples) + zeroFill * nextPowerOfTwo), 'constant', constant_values = 0)
				self.fftData = np.vstack([self.fftData, np.fft.fftshift(np.fft.fft(tmpData))])
	def getIndex(self, frequency):
		index = 0
		while self.frequencies[index] < frequency:
			index += 1
		return index

	def sum(self, startScan = 0, stopScan = None):
		if stopScan == None:
			stopScan = self.data[:,0].size-1
		elif stopScan >  self.data[:,0].size-1 or startScan < -1*self.data[:,0].size:
			print('Warning, summing over non-existant scans, number of scans is', self.data[:,0].size)
		if self.data.size==0:
		    print('Warning: No data found, did you run "data.read()"?')
		else:
		    self.summedData = np.sum(self.data[startScan:stopScan], axis=0)
	def fit(self, startFrequency, stopFrequency, scanNumber, function = 0, summed = 0) :
		startIndex = 0
		while self.frequencies[startIndex] < startFrequency:
			startIndex = startIndex + 1
		stopIndex = startIndex
		while self.frequencies[stopIndex] < stopFrequency:
			stopIndex = stopIndex + 1
		if function == 0:
			#def func(x, width, height, center):
			#	return height / (np.pi * (x - center)**2/width + (width))
			def func(x, *parameters):
			        #parameters[0] is width
			        #parameters[1] is frequency
			        #parameters[0] is width
				return parameters[0] / (np.pi * ((x - parameters[1])**2/parameters[2] + (parameters[2])))
		elif function == 1:
			def func(x, a, b, c):
				return a * np.exp(-b * x) + c
		else:
			print ('Please choose valid function: \n 0: lorentian\n 1: exponential')
		parameterBounds = ([-np.inf, startFrequency, -np.inf], [np.inf, stopFrequency, np.inf])
		if summed == 0:
			return func, curve_fit(func,
				self.frequencies[startIndex:stopIndex], np.real(cmath.exp(1j*self.phase[scanNumber]) * self.fftData[scanNumber,	-self.frequencies.size+startIndex:-self.frequencies.size+stopIndex]), self.fitParameters[scanNumber], maxfev = 2000, bounds=parameterBounds)
		elif summed == 1:
			#pdb.set_trace()
			return	func, curve_fit(func, self.frequencies[startIndex:stopIndex], np.real(cmath.exp(1j*self.summedPhase) * self.summedFftData[-self.frequencies.size+startIndex:-self.frequencies.size+stopIndex]), self.summedFitParameters, maxfev = 2000, bounds=parameterBounds)
	def readParameters(self):
		parameterFilePath = os.path.splitext(self.fullPath)[0] + 'FitParameters.dat'
		if os.path.exists(parameterFilePath) and os.path.getsize(parameterFilePath)>0:
			with open(parameterFilePath) as fullFile:
				lineNumber = 0
				readList  = list((float(number) for number in fullFile.readline().strip().split()))
				self.summedFitParameters = readList[0:len(readList) - 1]
				self.summedPhase = readList[len(readList) - 1]
				print(self.summedFitParameters)
				for line in fullFile:
					readList  = list((float(number) for number in line.strip().split()))
					self.fitParameters[lineNumber] = readList[0:len(readList) - 1]
					self.phase[lineNumber] = readList[len(readList) -1]
					lineNumber += 1 
				print("Read parameters from file.")
				print(self.phase)

	def saveParameters(self):
		noExtensionPath = os.path.splitext(self.fullPath)
		parameterFile = open(str(noExtensionPath[0]) + 'FitParameters.dat', 'w+')
		if np.any(self.summedFitParameters):
			parameterFile.write(str(self.summedFitParameters).lstrip('[').rstrip(']') + '\t')
			parameterFile.write(str(self.summedPhase))
			parameterFile.write(str('\n'))
		else:
			for column in range(0, self.fitParameters.shape[1]):
				#parameterFile.write('\t'.join("") + '\n')
				parameterFile.write("0\t")
			parameterFile.write(str(self.summedPhase))
			parameterFile.write(str('\n'))
		if self.fitParameters.any:
			for row in range(0,self.fitParameters.shape[0]):
				for column in range (0,self.fitParameters.shape[1]):
					parameterFile.write(str(self.fitParameters[row][column]) + "\t")
				parameterFile.write(str(self.phase[row]))
				parameterFile.write(str('\n'))
		else:
			for row in range(0,self.fitParameters.shape[0]):
				for column in range (0,self.fitParameters.shape[1]):
					parameterFile.write(str(self.fitParameters[row][column]) + "\t")
				parameterFile.write(str(self.phase[row]))
				parameterFile.write(str('\n'))
