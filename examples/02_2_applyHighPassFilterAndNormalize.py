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

import warnings

warnings.filterwarnings("ignore")


rootDir = "/tmp/working/KaggleBirdsongRecognition2020/"
# rootDir = '/net/mfnstore-lin/export/tsa_transfer/TrainData/KaggleBirdsongRecognition2020/'

srcDir = rootDir + "data/audio/01_wav_via_librosa/"
dstDir = rootDir + "data/audio/02_wav_filtered_and_normalized/"


def apply_high_pass_filter(input, sample_rate, fileName):

    order = 2
    cutoff_frequency = 2000

    sos = butter(
        order, cutoff_frequency, btype="highpass", output="sos", fs=sample_rate
    )
    output = sosfilt(sos, input, axis=0)

    # If anything went wrong (nan in array or max > 1.0 or min < -1.0) --> return original input
    if np.isnan(output).any() or np.max(output) > 1.0 or np.min(output) < -1.0:
        print("Warning filter:", fileName)
        output = input

    # print(type, order, np.min(input), np.max(input), np.min(output), np.max(output))

    return output


def readAndProcessWavFile(srcFid, dstDir):

    file = os.path.basename(srcFid)
    fileName = file[:-4]
    dstFid = dstDir + file

    # if True:
    if not os.path.isfile(dstFid):

        # Read wav file via soundfile
        y, sr = sf.read(srcFid)

        # print(fileName, sr, y.shape)

        # Normalize (to prevent filter errors)
        y /= np.max(y)
        y *= 0.5

        # Apply high pass filter (if no filter issues) and normalize to -3dB
        y = apply_high_pass_filter(y, sr, fileName)

        # Normalize to -3 dB
        y /= np.max(y)
        y *= 0.7071

        # Write result
        sf.write(dstFid, y, sr, "PCM_16")

        # # Use sox
        # subprocess.call(['sox', srcFid, dstFid, 'norm', '-5', 'highpass', '2000.0', 'norm', '-3'])


def proccesAllFilesInDir(srcDir):
    NumOfCoresToUse = -8
    NumOfCoresAvailable = multiprocessing.cpu_count()
    if NumOfCoresToUse > 0:
        NumOfJobs = NumOfCoresToUse
    else:
        NumOfJobs = NumOfCoresAvailable + NumOfCoresToUse
    print("NumOfCoresAvailable", NumOfCoresAvailable, "NumOfJobs", NumOfJobs)

    srcFids = []
    for file in os.listdir(srcDir):
        srcFid = srcDir + file
        # print(srcFid)
        srcFids.append(srcFid)

    # Test a few
    # srcFids = srcFids[:10]

    Parallel(n_jobs=NumOfJobs)(
        delayed(readAndProcessWavFile)(srcFid, dstDir) for srcFid in srcFids
    )


if __name__ == "__main__":

    TimeStampStart = time.time()

    proccesAllFilesInDir(srcDir)

    print("ElapsedTime [s]: ", (time.time() - TimeStampStart))
