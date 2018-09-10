import numpy as np
def fft(values, omitSamples):
	print('customFFT')
	return np.fft.fftshift(np.fft.fft(values[omitSamples:]))
