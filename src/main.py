import matplotlib.pyplot as plt
import numpy as np
import data, fft
parameters, data = data.read('/media/group/hyper/archive/Measured_Data/2016_02_25/20160225_180724.mat', 0)
#summedData = data.sum(data)
ftData = fft.fft(data[0,:], 0)
nSamples = parameters[0]
dwelltime = 1/parameters[1]
frequencies = np.linspace(0, 1/(2*dwelltime), nSamples)
plt.plot(frequencies, ftData)
plt.show()

