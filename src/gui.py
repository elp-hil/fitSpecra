import os
import cmath
import tkinter
import dataStruct
import matplotlib
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy as np
import pdb
#dataText = '/media/group/hyper/archive/Measured_Data/2016_06_21/20160621_081835.mat'
dataText = '/media/group/hyper/archive/Measured_Data/2018_09_17/125700.mat'
matplotlib.use("TkAgg")
class mainWindow:
	def __init__(self):
		self.scanNumber = 0
		self.top = tkinter.Tk()
		#main data text box
		self.dataTextBox = tkinter.Text(self.top, height=1, width=150)
		self.dataTextBox.insert(tkinter.END, dataText)
		self.dataTextBox.grid(row = 0, column = 0, sticky = tkinter.E+tkinter.W)
		#main figure
		self.figure = Figure(figsize = (5,5), dpi = 100)
		self.subplot = self.figure.add_subplot(111)
		self.plotCanvas = FigureCanvasTkAgg(self.figure, self.top)
		self.plotCanvas.get_tk_widget().grid(row = 1, column = 0, rowspan = 100,sticky = tkinter.E+tkinter.W+tkinter.N)
		#load data button
		self.loadDataButton = tkinter.Button(self.top, text = "load data", command = self.loadDataCallback)
		self.loadDataButton.grid(row = 2, column = 4, sticky = tkinter.E+tkinter.W+tkinter.N)
		self.fftDataButton = tkinter.Button(self.top, text = "fft data", command = self.fftGuiData)
		self.fftDataButton.grid(row = 4, column = 4, sticky = tkinter.E+tkinter.W+tkinter.N)
		#select scan number
		self.scanNumberFrame = tkinter.LabelFrame(self.top, text = "scan number")
		self.scanNumberFrame.grid(row = 3, column = 4, sticky = tkinter.E + tkinter.W)

		self.lowerScanNumberButton = tkinter.Button(self.scanNumberFrame, text = "-", command = self.lowerScanCallback)
		self.lowerScanNumberButton.grid(row = 0, column = 0, sticky = tkinter.W)

		self.scanNumberTextBox = tkinter.Text(self.scanNumberFrame, height = 1, width = 10)
		self.scanNumberTextBox.insert(tkinter.END, 0)
		self.scanNumberTextBox.grid(row = 0, column = 1, sticky = tkinter.W + tkinter.E)

		self.raiseScanNumberButton = tkinter.Button(self.scanNumberFrame, text = "+", command = self.raiseScanCallback)
		self.raiseScanNumberButton.grid(row = 0, column = 2, sticky = tkinter.E)

		#frequency limit user input in a frame
		self.frequencyInputFrame = tkinter.LabelFrame(self.top, text = "frequencies")
		self.frequencyInputFrame.grid(row = 5, column = 4)

		self.minFrequencyLabel = tkinter.Label(self.frequencyInputFrame, text = "f_min")
		self.minFrequencyLabel.grid(row = 0, column = 0, sticky = tkinter.E+ tkinter.W)

		self.minFrequencyString = tkinter.StringVar(self.top)
		self.minFrequencyString.set("241000")
		self.minFrequencyString.trace("w",lambda name,index, callback: self.plotWindow(self.scanNumber))

		self.minFrequencyEntry = tkinter.Entry(self.frequencyInputFrame, textvariable = self.minFrequencyString)
		self.minFrequencyEntry.grid(row = 1, column = 0, sticky = tkinter.E+tkinter.W+tkinter.N)
		self.maxFrequencyLabel = tkinter.Label(self.frequencyInputFrame, text = "f_max")
		self.maxFrequencyLabel.grid(row = 0, column = 1, sticky = tkinter.E+ tkinter.W)

		self.maxFrequencyString = tkinter.StringVar(self.top)
		self.maxFrequencyString.set("245000")
		self.maxFrequencyString.trace("w",lambda name,index, callback: self.plotWindow(self.scanNumber))
		self.maxFrequencyEntry = tkinter.Entry(self.frequencyInputFrame, textvariable = self.maxFrequencyString)
		self.maxFrequencyEntry.grid(row = 1, column = 1, sticky = tkinter.E+tkinter.W+tkinter.N)

		#settings in a frame
		self.settingsFrame = tkinter.LabelFrame(self.top, text = "settings")
		self.settingsFrame.grid(row = 6, column = 4, sticky = tkinter.E+tkinter.W)
		#omit samples textbox
		self.omitSamplesLabel = tkinter.Label(self.settingsFrame, text = "samples omitted")
		self.omitSamplesLabel.grid(row = 0, column = 0, sticky = tkinter.S)
		self.omitSamplesTextBox = tkinter.Text(self.settingsFrame, height=1, width=15)
		self.omitSamplesTextBox.insert("1.0",'1999')
		self.omitSamplesTextBox.grid(row = 1, column = 0, sticky = tkinter.E+tkinter.W+tkinter.N)
		#zerofill dropdown
		self.zeroFillLabel = tkinter.Label(self.settingsFrame, text = "zerofilling")
		self.zeroFillLabel.grid(row = 0, column = 1, sticky = tkinter.S)
		self.zeroFillStringVar = tkinter.StringVar(self.settingsFrame)
		self.zeroFillStringVar.set("0")
		self.zeroFillStringVar.trace("w",lambda name,index, callback: self.fftGuiData())
		self.zeroFillOptionMenu = tkinter.OptionMenu(self.settingsFrame, self.zeroFillStringVar, "0", "1", "2")
		self.zeroFillOptionMenu.grid(row = 1, column = 1, sticky = tkinter.E+tkinter.W+tkinter.N)
		#sum data checkbox
		self.sumDataVar = tkinter.IntVar()
		self.sumDataCheckbox = tkinter.Checkbutton(self.settingsFrame, text = "sum data", variable = self.sumDataVar)
		self.sumDataCheckbox.grid(row = 2, column = 0)
		#phase setting
		self.phaseFrame = tkinter.LabelFrame(self.top, name = "phase")
		self.phaseFrame.grid(row = 8, column = 4, sticky = tkinter.W + tkinter.E)
		self.phaseStringVar = tkinter.StringVar(self.phaseFrame)
		self.phaseSlider = tkinter.Scale(self.phaseFrame, from_= -np.pi, to= np.pi, resolution = 0.1, variable = self.phaseStringVar, orient = tkinter.HORIZONTAL)
		self.phaseStringVar.trace("w", lambda name, index, callback:self.setPhase(self.scanNumber))
		self.phaseSlider.grid(row = 0, column = 0, sticky = tkinter.W+tkinter.E)
		#fit function choice
		self.fitFrame = tkinter.LabelFrame(self.top, text= "fit")
		fitFunctionChoice = tkinter.StringVar(self.fitFrame)
		self.fitFunctionDropdown = tkinter.OptionMenu(self.fitFrame, fitFunctionChoice, "lorentian")
		#fit data button
		self.fitDataButton = tkinter.Button(self.top, text = 'fit data', command = self.fitGuiData)
		self.fitDataButton.grid(row = 7, column = 4, sticky = tkinter.W + tkinter.E)
		#fitParameters
		self.fitParametersFrame = tkinter.LabelFrame(self.top, text = "fit parameters")
		self.fitParametersFrame.grid(row = 9, column = 4)
		self.frequencyParameterLabel = tkinter.Label(self.fitParametersFrame, text = "frequency")
		self.widthParameterLabel = tkinter.Label(self.fitParametersFrame, text = "width")
		self.heightParameterLabel = tkinter.Label(self.fitParametersFrame, text = "height")
		self.frequencyParameter = tkinter.Entry(self.fitParametersFrame)
		self.widthParameter = tkinter.Entry(self.fitParametersFrame)
		self.heightParameter = tkinter.Entry(self.fitParametersFrame)
		self.frequencyParameterLabel.grid(row = 0, column = 0)
		self.widthParameterLabel.grid(row = 0, column = 1)
		self.heightParameterLabel.grid(row = 0, column = 2)
		self.frequencyParameter.grid(row = 1, column = 0)
		self.widthParameter.grid(row = 1, column = 1)
		self.heightParameter.grid(row = 1, column = 2)
		#close main Window
		self.closeButton = tkinter.Button(self.top, text = "close", command = self.closeCallback)
		self.closeButton.grid(row = 0, column = 4, sticky = tkinter.E+tkinter.W+tkinter.N)
		#brose for data files
		self.browseButton = tkinter.Button(self.top, text = "browse", command = self.browseCallback)
		self.browseButton.grid(row = 1, column = 4, sticky = tkinter.E+tkinter.W+tkinter.N)
		#invoke main window
		self.top.mainloop()
	def browseCallback(self):
		newDataFile =  filedialog.askopenfilename(initialdir = '/media/group/hyper/archive/Measured_Data/', title = 'Please select a file')
		self.dataTextBox.delete("1.0", tkinter.END)
		self.dataTextBox.insert(tkinter.END, newDataFile)
	def loadDataCallback(self):
		self.scanNumber = 0
		self.dataString = self.dataTextBox.get("1.0", tkinter.END).strip()
		self.guiData = dataStruct.data(self.dataString)
		self.guiData.read()
		self.fftGuiData()
		self.readParameters()
		self.plotWindow(0)
	def readParameters(self):
		parameterFilePath = os.path.splitext(self.guiData.fullPath)[0] + 'FitParameters.dat'
		if os.path.exists(parameterFilePath) and os.path.getsize(parameterFilePath)>0:
			with open(parameterFilePath) as fullFile:
				lineNumber = 0
				fullFile.readline().strip().split("\t")
				for line in fullFile:
					self.guiData.fitParameters[lineNumber] =line.strip().split("\t")
					print(line)
					lineNumber += 1
					print("Read parameters from file.")

	def saveParameters(self):
		noExtensionPath = os.path.splitext(self.guiData.fullPath)
		parameterFile = open(str(noExtensionPath[0]) + 'FitParameters.dat', 'w+')
		if np.any(self.guiData.summedFitParameters):
			parameterFile.write(str(self.guiData.summedFitParameters))
			parameterFile.write(str('\n'))
		else:
			for column in range(0, self.guiData.fitParameters.shape[1]):
				parameterFile.write('\t'.join("") + '\n')
				parameterFile.write("0\t")
			parameterFile.write(str('\n'))
		if self.guiData.fitParameters.any:
			for row in range(0,self.guiData.fitParameters.shape[0]):
				for column in range (0,self.guiData.fitParameters.shape[1]):
					parameterFile.write(str(self.guiData.fitParameters[row][column]) + "\t")
				parameterFile.write(str('\n'))
		else:
			for row in range(0,self.guiData.fitParameters.shape[0]):
				for column in range (0,self.guiData.fitParameters.shape[1]):
					parameterFile.write(str(self.guiData.fitParameters[row][column]) + "\t")
				parameterFile.write(str('\n'))
	def fftGuiData(self):
		print("zerofilling: ", self.zeroFillStringVar.get())
		print(self.sumDataVar.get())
		self.guiData.fft(omitSamples = int(self.omitSamplesTextBox.get("1.0",tkinter.END).strip()), sumScans = self.sumDataVar.get(), zeroFill = int(self.zeroFillStringVar.get()))
		if self.sumDataVar.get():
			self.plotWindow(0)
		else:
			self.plotWindow(self.scanNumber)
	def raiseScanCallback(self):
		if self.scanNumber < self.guiData.data.shape[0]-1:
			self.scanNumber +=1
			self.plotWindow(self.scanNumber)
			self.scanNumberTextBox.delete("1.0", tkinter.END)
			self.scanNumberTextBox.insert("1.0", self.scanNumber)
	def lowerScanCallback(self):
		if self.scanNumber > 0:
			self.scanNumber -=1
			self.plotWindow(self.scanNumber)
			self.scanNumberTextBox.delete("1.0", tkinter.END)
			self.scanNumberTextBox.insert("1.0", self.scanNumber)
	def fitFunction(self, data, *parameters):
		return np.zeros(data.shape[0]) #real fit function is returned by guiData.fit
	def setPhase(self, scanNumber):
		if self.sumDataVar.get():
			self.guiData.phase[0] = float(self.phaseStringVar.get())
			self.plotWindow(self.scanNumber)
		else:
			self.guiData.phase[scanNumber] = float(self.phaseStringVar.get())
			self.plotWindow(self.scanNumber)
	def fitGuiData(self):
		frequency = float(self.frequencyParameter.get()) if self.frequencyParameter.get() else (int(self.maxFrequencyEntry.get())+int(self.minFrequencyEntry.get()))/2
		width = float(self.widthParameter.get()) if self.widthParameter.get() else (int(self.maxFrequencyEntry.get())-int(self.minFrequencyEntry.get()))/100
		#height = self.heightParameter.get() if self.heightParameter.get() else np.max(self.guiData.fftData[self.scanNumber])
		if self.heightParameter.get():
			height = float(self.heightParameter.get())
		elif self.guiData.summedFftData.any():
			height = np.real(np.max(self.guiData.summedFftData[self.guiData.getIndex(int(self.minFrequencyEntry.get())):self.guiData.getIndex(int(self.maxFrequencyEntry.get()))]))
		elif self.guiData.fftData.any():
			height = np.real(np.max(self.guiData.fftData[self.scanNumber, self.guiData.getIndex(int(self.minFrequencyEntry.get())):self.guiData.getIndex(int(self.maxFrequencyEntry.get()))]))
		else:
			height = 1;
		if self.sumDataVar.get():
			self.guiData.summedFitParameters = [height, frequency, width]
		else:
			self.guiData.fitParameters[self.scanNumber] = [height, frequency, width]
		self.fitFunction, tempParameters = self.guiData.fit(int(self.minFrequencyEntry.get()), int(self.maxFrequencyEntry.get()), self.scanNumber, 0, self.sumDataVar.get())
		print("tempParameters: ")
		print(tempParameters)
		if self.sumDataVar.get():
			self.guiData.summedFitParameters = tempParameters[0]
		else:
			self.guiData.fitParameters[self.scanNumber] = tempParameters[0]
		self.frequencyParameter.delete(0,tkinter.END)
		self.widthParameter.delete(0,tkinter.END)
		self.heightParameter.delete(0,tkinter.END)
		self.frequencyParameter.insert(0, tempParameters[0][1])
		self.widthParameter.insert(0,tempParameters[0][2])
		self.heightParameter.insert(0, tempParameters[0][0])

		self.plotWindow(self.scanNumber)
		self.saveParameters()
	def callback(self, *args):
		print("callback called")
	def plotWindow(self, scanNumber):
		self.heightParameter.delete(0,tkinter.END)
		self.widthParameter.delete(0,tkinter.END)
		self.frequencyParameter.delete(0,tkinter.END)
		try:
			self.subplot.clear()
			if self.guiData:
				lowerIndex = self.guiData.getIndex(int(self.minFrequencyEntry.get()))
				upperIndex = self.guiData.getIndex(int(self.maxFrequencyEntry.get()))
				print("lower: ", lowerIndex, "upper: ", upperIndex, "sumData: ", self.sumDataVar.get())
			if self.sumDataVar.get():
				print("size summed fft: ", self.guiData.summedFftData.size)
				self.subplot.plot(self.guiData.frequencies[lowerIndex:upperIndex], np.real(cmath.exp(1j*self.guiData.phase[0])*  self.guiData.summedFftData[-self.guiData.frequencies.size+lowerIndex:-self.guiData.frequencies.size+upperIndex]))
				#pdb.set_trace()
				#self.subplot.plot(self.guiData.frequencies[lowerIndex:upperIndex], np.real(cmath.exp(1j*self.guiData.phase[0])*  np.sum(self.guiData.fftData[:, -self.guiData.frequencies.size+lowerIndex:-self.guiData.frequencies.size+upperIndex])))
				#self.subplot.plot(self.guiData.timePoints[lowerIndex:upperIndex] , np.real( self.guiData.data[0, lowerIndex:upperIndex ]))
				print(self.guiData.summedFitParameters)
				if np.any(self.guiData.summedFitParameters):
					yData = np.real(cmath.exp(1j*self.guiData.phase[0]) * self.fitFunction(self.guiData.frequencies[lowerIndex:upperIndex], *self.guiData.summedFitParameters))
					self.subplot.plot(self.guiData.frequencies[lowerIndex:upperIndex], yData)
			else:
				if self.guiData.fitParameters[self.scanNumber].any():
					print("params:", self.guiData.fitParameters)
					self.heightParameter.insert(0,self.guiData.fitParameters[self.scanNumber][0])
					self.widthParameter.insert(0,self.guiData.fitParameters[self.scanNumber][2])
					self.frequencyParameter.insert(0,self.guiData.fitParameters[self.scanNumber][1])
				self.subplot.plot(self.guiData.frequencies[lowerIndex:upperIndex], np.real(cmath.exp(1j*self.guiData.phase[scanNumber]) * self.guiData.fftData[scanNumber, -self.guiData.frequencies.size+lowerIndex:-self.guiData.frequencies.size+upperIndex]))
				if np.any(self.guiData.fitParameters[scanNumber]):
					yData = np.real(cmath.exp(1j*self.guiData.phase[0]) * self.fitFunction(self.guiData.frequencies[lowerIndex:upperIndex], *self.guiData.fitParameters[scanNumber]))
					self.subplot.plot(self.guiData.frequencies[lowerIndex:upperIndex], yData)
			self.plotCanvas.draw()
		except AttributeError:
			print("Please load a dataset")
		except IndexError:
			print("Please check parameters")
		except ValueError:
			print("wrong parameters entered")
		#self.minFrequencyEntry.focus_set()
	def closeCallback(self):
		self.top.destroy()
