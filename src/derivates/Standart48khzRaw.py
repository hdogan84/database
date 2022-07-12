from derivates.DerivativeBaseClasss import DerivativeBaseClass
from logging import debug, warn
from tools.configuration import DatabaseConfig
from typing import List, Dict
from pathlib import Path
import librosa
from librosa import resample
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
import warnings

sampleRateDst = 48000  # 32000


class Standart48khzRaw(DerivativeBaseClass):
    name = "Standart48khzRaw"
    sample_rate: int = sampleRateDst
    resampleType = "kaiser_best"  # "kaiser_fast"  # or use
    bit_depth: int = 16
    file_ending: str = "wav"
    description: str = ""

    def __init__(self, config: DatabaseConfig):
        super(Standart48khzRaw, self).__init__(config)

    def create_derivate(
        self,
        source_file_path: Path,
        target_file_path: Path,
    ) -> None:
        # resample on load to higher prevent instability of the filter
        # print("Read: {} \n write to: ".format(source_file_path))
        y = []

        y, sr = librosa.load(
            source_file_path,
            sr=None,
            mono=False,
            res_type=self.resampleType,
        )
        if np.isfinite(y).all() is False:
            raise Exception("Error creating derivative for {}".format(source_file_path))
            return

        if sr != self.sample_rate:
            y = librosa.resample(
                y,
                sr,
                self.sample_rate,
                res_type=self.resampleType,
            )
        if len(y.shape) > 1:
            y = np.transpose(y)  # [nFrames x nChannels] --> [nChannels x nFrames]
            # print("write to target_file_path: {}".format(target_file_path))

        sf.write(target_file_path, y, self.sample_rate, "PCM_16")
