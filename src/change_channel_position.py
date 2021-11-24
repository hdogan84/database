import csv
import random
import librosa
from pathlib import Path
import argparse
from os import listdir, mkdir
from os.path import isfile, join
import soundfile as sf
import numpy as np

# This script split a given csv in train and validation csv


def change_channel_position(
    source_directory: str, target_directory: str, order=[1, 0, 2, 3]
):
    try:
        mkdir(target_directory)
    except FileExistsError:
        pass
    files = [
        f
        for f in listdir(source_directory)
        if (isfile(join(source_directory, f)) and f.endswith(".wav"))
    ]

    for file in files:
        source_filepath = join(source_directory, file)
        target_filepath = join(target_directory, file)
        y, sr = librosa.load(source_filepath, mono=False, sr=None)
        output = np.array([y[order[0]], y[order[1]], y[order[2]], y[order[3]]])
        # sf.write('stereo_file.wav', np.random.randn(100000, 2), sr, 'PCM_24')
        print(sr)
        sf.write(target_filepath, output.T, sr, "PCM_16")
        print(target_filepath)


parser = argparse.ArgumentParser(description="")


args = parser.parse_args()
if __name__ == "__main__":
    change_channel_position(
        "/mnt/z/Projekte/AMMOD/AudioData/BRITZ02/Britz02_2021_04/",
        "/mnt/z/Projekte/AMMOD/AudioData/BRITZ02/Britz02_2021_04_reordered/",
    )
