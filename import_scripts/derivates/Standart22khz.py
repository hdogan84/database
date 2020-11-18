from derivates.DerivativeBaseClasss import DerivativeBaseClass
from logging import debug
from tools.configuration import DatabaseConfig
from typing import List, Dict
from pathlib import Path
import librosa
import numpy as np
import soundfile as sf

sampleRateDst = 32000  # 32000
resampleType = "kaiser_fast"  # 'kaiser_best'


class Standart22khz(DerivativeBaseClass):
    name = "Standart22khzNormalisedHighpassFilter"
    sample_rate: int = 32000
    bit_depth: int = 16
    file_ending: str = "wav"
    description: str = "Normalisez to 0.7071;  Highpass filter: "

    def __init__(self, config: DatabaseConfig):
        super(Standart22khz, self).__init__(config)

    def create_derivate(
        self,
        source_file_path: Path,
        target_file_path: Path,
    ) -> None:
        y, _ = librosa.load(
            source_file_path, sr=sampleRateDst, mono=False, res_type=resampleType
        )
        # Normalize to -3 dB
        y /= np.max(y)
        y *= 0.7071
        if len(y.shape) > 1:
            y = np.transpose(y)  # [nFrames x nChannels] --> [nChannels x nFrames]
        sf.write(target_file_path, y, sampleRateDst, "PCM_16")

        debug("standart22khz {}".format(target_file_path.as_posix()))
