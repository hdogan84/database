# Kaggle docker image
# WORKING=/net/mfnstore-lin/export/tsa_transfer/TrainData
# docker run --runtime nvidia -v $WORKING:/tmp/working -w=/tmp/working --rm --ipc=host -it gcr.io/kaggle-gpu-images/python /bin/bash
# cd /tmp/working/KaggleBirdsongRecognition2020/src

import os
import time
import numpy as np
import librosa
import soundfile as sf

import ntpath
import subprocess
import multiprocessing
from joblib import Parallel, delayed

import warnings
warnings.filterwarnings('ignore')




rootDir = '/tmp/working/KaggleBirdsongRecognition2020/'
#rootDir = '/net/mfnstore-lin/export/tsa_transfer/TrainData/KaggleBirdsongRecognition2020/'


# srcRootDir = rootDir + 'input/birdsong-recognition/train_audio/'
# dstDir = rootDir + 'data/audio/01_wav/'



def convertMp3ToWavViaLame(srcFid, dstDir):
	file = os.path.basename(srcFid)
	fileName = file[:-4]
	dstFid = dstDir + fileName + '.wav'
	subprocess.call(['lame', '--decode', srcFid, dstFid, '--quiet'])


def convertMp3ToWavViaLibrosa(srcFid, dstDir):

	file = os.path.basename(srcFid)
	fileName = file[:-4]
	dstFid = dstDir + fileName + '.wav'

	if not os.path.isfile(dstFid):

		try:
			warnings.filterwarnings('ignore')
			y, sr = librosa.load(srcFid, sr=None, mono=False)

			# Transpose if multi-channel (to get correct format for writing via soundfile)
			if len(y.shape) > 1:
				y = y.T

			# Write audio file
			sf.write(dstFid, y, sr, 'PCM_16')

		except Exception as ex:
			print('Error', fileName, ex)



def convertParallel():

	NumOfCoresToUse = -8
	NumOfCoresAvailable = multiprocessing.cpu_count()
	if NumOfCoresToUse > 0: NumOfJobs = NumOfCoresToUse
	else: NumOfJobs = NumOfCoresAvailable + NumOfCoresToUse
	print('NumOfCoresAvailable', NumOfCoresAvailable, 'NumOfJobs', NumOfJobs)

	# Get subdirs
	classIds = os.listdir(srcRootDir)
	srcFids = []

	for ix in range(len(classIds)):
		#if ix > 1: break
		classId = classIds[ix]
		srcDir = srcRootDir + classId + '/'
		for file in os.listdir(srcDir):
			srcFid = srcDir + file
			srcFids.append(srcFid)
			#print(classId, file)

	Parallel(n_jobs=NumOfJobs)(delayed(convertMp3ToWavViaLibrosa)(srcFid, dstDir) for srcFid in srcFids)
			

def convertAllInDirParallel():

	NumOfCoresToUse = -8
	NumOfCoresAvailable = multiprocessing.cpu_count()
	if NumOfCoresToUse > 0: NumOfJobs = NumOfCoresToUse
	else: NumOfJobs = NumOfCoresAvailable + NumOfCoresToUse
	print('NumOfCoresAvailable', NumOfCoresAvailable, 'NumOfJobs', NumOfJobs)

	srcFids = []

	for file in os.listdir(srcRootDir):
		srcFid = srcRootDir + file
		srcFids.append(srcFid)
		#print(classId, file)

	Parallel(n_jobs=NumOfJobs)(delayed(convertMp3ToWavViaLibrosa)(srcFid, dstDir) for srcFid in srcFids)


if __name__ == "__main__":

	TimeStampStart = time.time() # for performance measurement

	#convertParallel()
	convertAllInDirParallel()

	# Use lame for train_audio/lotduc/XC195038.mp3
	#convertMp3ToWavViaLame(srcRootDir + 'lotduc/XC195038.mp3', dstDir)


	print('ElapsedTime [s]: ', (time.time() - TimeStampStart))
	
