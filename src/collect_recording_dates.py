from datetime import datetime
from pathlib import Path
from tools.file_handling.name import parse_filename_for_location_date_time
import csv
import librosa


def scan_file_list(file_list):
    if isinstance(file_list, str):  # if string is presented convert to list
        file_list = [file_list]
    result = []
    for filepath in file_list:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        if filepath.is_dir():
            if filepath.as_posix().endswith("reordered"):
                pass
            else:
                result = result + scan_file_list(list(filepath.iterdir()))

        else:
            if filepath.as_posix().endswith("(Kopie).wav"):
                pass
            elif filepath.suffix == ".wav" or filepath.suffix == ".mp3":

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
    print("Found {} files create csv".format(len(file_list)))
    result = []
    headline = [
        "filepath",
        "filename",
        "location",
        "datetime",
        "date",
        "time",
        "duration(s)",
        "size",
    ]
    for filepath in file_list:
        parsed_values = parse_filename_for_location_date_time(filepath.stem)
        try:
            duration = librosa.get_duration(filename=filepath)
            result.append(
                [
                    filepath.as_posix(),
                    filepath.name,
                    parsed_values.location_name,
                    parsed_values.record_datetime.strftime("%Y/%m/%d, %H:%M:%S"),
                    parsed_values.record_datetime.strftime("%Y/%m/%d"),
                    parsed_values.record_datetime.strftime("%H:%M:%S"),
                    duration,
                    Path(filepath).stat().st_size,
                ]
            )
        except Exception as err:
            print("Broken file {}".format(filepath.as_posix()))
            print(err)
    result.sort(key=sortKey)
    write_results_to_file(output_file, headline, result)


# collect_data("/mnt/z/Projekte/AMMOD/AudioData/BRITZ02/", "BRITZ02_overview.csv")

# collect_data("/mnt/z/Projekte/AMMOD/AudioData/BRITZ01/", "BRITZ01_overview.csv")
collect_data("/mnt/z/Projekte/AMMOD/AudioData/BRITZ03/", "BRITZ03_overview.csv")
# collect_data("/mnt/z/Projekte/AMMOD/AudioData/Schoenow01/", "Schoenow01_overview.csv")
# collect_data("/mnt/z/Projekte/AMMOD/AudioData/MGB01/", "MGB01_overview.csv")
# collect_data("dummy", "dummy.csv")
