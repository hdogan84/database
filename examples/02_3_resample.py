# Kaggle docker image
# WORKING=/net/mfnstore-lin/export/tsa_transfer/TrainData
# docker run --runtime nvidia -v $WORKING:/tmp/working -w=/tmp/working --rm --ipc=host -it gcr.io/kaggle-gpu-images/python /bin/bash
# cd /tmp/working/KaggleBirdsongRecognition2020/src

import os
import time
import numpy as np
import soundfile as sf


from scipy.signal import butter, sosfilt

import ntpath
import subprocess
import multiprocessing
from joblib import Parallel, delayed

import librosa
#import warnings
#warnings.filterwarnings('ignore')





rootDir = '/tmp/working/KaggleBirdsongRecognition2020/'
#rootDir = '/net/mfnstore-lin/export/tsa_transfer/TrainData/KaggleBirdsongRecognition2020/'

srcDir = rootDir + 'data/audio/02_wav_filtered_and_normalized/'


# 32000 Hz
dstDir = rootDir + 'data/audio/13_wav_filtered_and_normalized_32000Hz_kaiser_fast/'
sampleRateDst = 32000	# 32000
resampleType = 'kaiser_fast' # 'kaiser_best'





def readAndProcessWavFile(srcFid, dstDir):

	file = os.path.basename(srcFid)
	fileName = file[:-4]
	dstFid = dstDir + file

	
	#if True:
	if not os.path.isfile(dstFid):

		# # Use sf.read

		# # Read wav file via soundfile
		# y, sampleRateSrc = sf.read(srcFid)
		# if len(y.shape) > 1:
		# 	y = np.transpose(y) # [nFrames x nChannels] --> [nChannels x nFrames]

		# print(fileName, sampleRateSrc, y.shape, len(y.shape))

		# # Resample
		# y = np.asfortranarray(y)
		# if sampleRateSrc != sampleRateDst:
		# 	y = librosa.resample(y, sampleRateSrc, sampleRateDst, res_type=resampleType)


		# Use librosa (read and resample in one)
		y, sr = librosa.load(srcFid, sr=sampleRateDst, mono=False, res_type=resampleType)

		# Normalize to -3 dB
		y /= np.max(y)
		y *= 0.7071


		#librosa.output.write_wav(dstFid, y, sr)
		
		# Write result
		if len(y.shape) > 1:
			y = np.transpose(y) # [nFrames x nChannels] --> [nChannels x nFrames]
		sf.write(dstFid, y, sampleRateDst, 'PCM_16')





def proccesAllFilesInDir(srcDir):

	NumOfCoresToUse = -8
	NumOfCoresAvailable = multiprocessing.cpu_count()
	if NumOfCoresToUse > 0: NumOfJobs = NumOfCoresToUse
	else: NumOfJobs = NumOfCoresAvailable + NumOfCoresToUse
	print('NumOfCoresAvailable', NumOfCoresAvailable, 'NumOfJobs', NumOfJobs)

	srcFids = []
	for file in os.listdir(srcDir):
		srcFid = srcDir + file
		#print(srcFid)
		srcFids.append(srcFid)


	# Test a few
	#srcFids = srcFids[:10]

	Parallel(n_jobs=NumOfJobs)(delayed(readAndProcessWavFile)(srcFid, dstDir) for srcFid in srcFids)





if __name__ == "__main__":


	TimeStampStart = time.time()

	proccesAllFilesInDir(srcDir)

	print('ElapsedTime [s]: ', (time.time() - TimeStampStart))
	
