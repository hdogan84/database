from datetime import datetime
from pathlib import Path
from tools.file_handling.name import parse_filename_for_location_date_time
import csv
import librosa
import numpy as np
import soundfile as sf


SAMPLE_RATE = 32000
BACKEND = "soundfile"


def scan_file_list(file_list):
    if isinstance(file_list, str):  # if string is presented convert to list
        file_list = [file_list]
    result = []

    for filepath in file_list:

        if isinstance(filepath, str):
            filepath = Path(filepath)

        if filepath.is_dir():
            result = result + scan_file_list(list(filepath.iterdir()))
        else:
            if BACKEND == "soundfile":
                audio_data, file_sample_rate = sf.read(
                    filepath, start=0, always_2d=True
                )
                audio_data = np.transpose(audio_data)

            elif BACKEND == "librosa":
                audio_data, sr = librosa.load(
                    filepath, offset=0, sr=SAMPLE_RATE, dtype=np.float32, mono=False
                )

            if len(audio_data.shape) == 1:
                audio_data = np.array([audio_data])

            if audio_data.shape[1] == 0:
                print(filepath)
                result.append(filepath)

    return result


def write_results_to_file(filepath, headline, data):
    with open(filepath, mode="w") as filewriter:
        writer = csv.writer(
            filewriter, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(headline)
        writer.writerows(data)


def sortKey(elem):
    return elem[1]


def collect_data(folder_path, output_file):
    print("Start collecting files {}".format(folder_path))
    file_list = scan_file_list([folder_path])

    write_results_to_file(output_file, ["filepath"], file_list)


collect_data(
    "/mnt/tsa_transfer/TrainData/libro_animalis/derivation/1", "broken_derivate.csv"
)

# collect_data("/mnt/z/Projekte/AMMOD/AudioData/BRITZ01/", "BRITZ01_overview.csv")
# collect_data("/mnt/z/Projekte/AMMOD/AudioData/BRITZ03/", "BRITZ03_overview.csv")
# collect_data("/mnt/z/Projekte/AMMOD/AudioData/Schoenow01/", "Schoenow01_overview.csv")
# collect_data("/mnt/z/Projekte/AMMOD/AudioData/MGB01/", "MGB01_overview.csv")
# collect_data("dummy", "dummy.csv")
