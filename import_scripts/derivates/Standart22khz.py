from derivates.DerivativeBaseClasss import DerivativeBaseClass
from logging import debug, warn
from tools.configuration import DatabaseConfig
from typing import List, Dict
from pathlib import Path
import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

sampleRateDst = 32000  # 32000
resampleType = "kaiser_fast"  # 'kaiser_best'


class Standart22khz(DerivativeBaseClass):
    name = "Standart22khzNormalisedHighpassFilter"
    sample_rate: int = 32000
    bit_depth: int = 16
    file_ending: str = "wav"
    description: str = "Normalised: 0.7071;  Highpass: butter, cutoff 2000Hz; "

    def __init__(self, config: DatabaseConfig):
        super(Standart22khz, self).__init__(config)

    def apply_high_pass_filter(self, input, sample_rate: int, filePath: Path):
        order = 2
        cutoff_frequency = 2000

        sos = butter(
            order, cutoff_frequency, btype="highpass", output="sos", fs=sample_rate
        )
        output = sosfilt(sos, input, axis=0)

        # If anything went wrong (nan in array or max > 1.0 or min < -1.0) --> return original input
        if np.isnan(output).any() or np.max(output) > 1.0 or np.min(output) < -1.0:
            warn("Warning filter: {}".format(filePath.as_posix()))
            output = input

        # print(type, order, np.min(input), np.max(input), np.min(output), np.max(output))

        return output

    def create_derivate(
        self,
        source_file_path: Path,
        target_file_path: Path,
    ) -> None:
        y, sr = librosa.load(
            source_file_path, sr=sampleRateDst, mono=False, res_type=resampleType
        )
        # Normalize to -3 dB
        y /= np.max(y)
        y *= 0.7071

        y = self.apply_high_pass_filter(y, sr, source_file_path)

        if len(y.shape) > 1:
            y = np.transpose(y)  # [nFrames x nChannels] --> [nChannels x nFrames]
        sf.write(target_file_path, y, sampleRateDst, "PCM_16")

        debug("standart22khz {}".format(target_file_path.as_posix()))
