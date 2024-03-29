from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path

from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from derivates.Standart22050hz_Highpass100Hz import Standart22050hz_Highpass100Hz as Derivate6
import argparse
from tools.file_handling.csv import write_to_csv
from enum import Enum, IntEnum
from export_scripts.export_tools import map_filename_to_derivative_filepath

CONFIG_FILE_PATH = Path("config_training.cfg")
noise_id_list = """
(
    5
)
"""
query_files = """
SELECT 
    distinct(r.filename), r.file_path
FROM
    annotation_of_noise AS a
        LEFT JOIN
    noise AS n ON n.id = a.noise_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
WHERE
    r.collection_id = 176 and
    n.id IN {}

""".format(
    noise_id_list
)

query_annoations = """
SELECT 
    n.name,
    r.file_path,
	r.filename,
    a.start_time,
    a.end_time,
    a.quality_tag,
    a.individual_id,
    a.group_id,
    a.vocalization_type,
    r.channels,
    r.collection_id,
    r.duration,
    i.id,
    i.start_time,
    i.end_time,
    r.original_filename,
    r.id
    
FROM
    annotation_of_noise AS a
        LEFT JOIN
    noise AS n ON n.id = a.noise_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
        LEFT JOIN
    annotation_interval AS i ON i.id = a.annotation_interval_id 
WHERE
    r.collection_id = 176 and 
    r.date LIKE '2022%' and 
    n.id IN {}
ORDER BY r.filename , a.start_time ASC
""".format(
    noise_id_list
)

query_species = """
SELECT name FROM libro_animalis.noise where
    id IN {}
ORDER BY name ASC
""".format(
    noise_id_list
)


class Index(IntEnum):
    LATIN_NAME = 0
    FILE_PATH = 1
    FILENAME = 2
    START_TIME = 3
    END_TIME = 4
    QUALITY_TAG = 5
    INDIVIDUAL_TAG = 6
    GROUP_ID = 7
    VOCALIZATION_TYPE = 8
    CHANNELS = 9
    COLLECTION_ID = 10
    DURATION = 11
    ANNOTATION_INTERVAL_ID = 12
    ANNOTATION_INTERVAL_START = 13
    ANNOTATION_INTERVAL_END = 14
    ORIGINAL_FILENAME = 15


def create_file_derivates(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_files)
            data = db_cursor.fetchall()
            filepathes = list(map(lambda x: (Path(x[1]).joinpath(x[0])), data))
            derivatateCreator = Derivate6(config.database)
            file_derivates_dict = derivatateCreator.get_original_derivate_dict(
                filepathes
            )
            return file_derivates_dict


def annotation_to_label(annotation):
    collection_id = annotation[Index.COLLECTION_ID]
    channels = annotation[Index.CHANNELS]
    duration = annotation[Index.END_TIME] - annotation[Index.START_TIME]
    start = annotation[Index.START_TIME]
    stop = annotation[Index.END_TIME]
    label = annotation[Index.LATIN_NAME]
    filename = annotation[Index.FILENAME]
    original_fname = annotation[Index.ORIGINAL_FILENAME]
    # return (duration, start, stop, label, 1, filename, channels, collection_id)
    return (
        Path(filename).stem,
        filename,
        channels,
        collection_id,
        label,
        start,
        stop,
        original_fname,
    )


def create_annoation_interval_label(annotation_list):
    # take first element in list to estimate annoation interval start
    annotation = annotation_list[0]
    collection_id = annotation[Index.COLLECTION_ID]
    channels = annotation[Index.CHANNELS]
    duration = annotation[Index.DURATION]
    original_fname = annotation[Index.ORIGINAL_FILENAME]

    start = (
        annotation[Index.ANNOTATION_INTERVAL_START]
        if annotation[Index.ANNOTATION_INTERVAL_ID] is not None
        else annotation[Index.START_TIME]
    )
    start = 0.0
    stop = (
        annotation[Index.ANNOTATION_INTERVAL_END]
        if annotation[Index.ANNOTATION_INTERVAL_ID] is not None
        else annotation[Index.DURATION]
    )
    label = "annotation_interval"
    filename = annotation[Index.FILENAME]
    return (
        Path(filename).stem,
        filename,
        channels,
        collection_id,
        label,
        start,
        stop,
        original_fname,
    )


def create_labels(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_annoations)
            data = db_cursor.fetchall()
            print("Found {} annotations".format(len(data)))

            labels = []
            intervals = {}
            # Collect Labels of Different record intervalls
            for a in data:
                if a[12] is None:
                    if str(a[15]) in intervals:

                        intervals[str(a[15])].append(a)
                    else:
                        intervals.update({str(a[15]): [a]})
                else:
                    if str(a[12]) in intervals:

                        intervals[str(a[12])].append(a)
                    else:
                        intervals.update({str(a[12]): [a]})
            # sort every key by start -, stop time
            for k, v in intervals.items():
                # only sort real intervals
                if k is not "None":
                    v.sort(key=lambda l: (l[3], l[4]), reverse=False)
            labels = []
            for key, values in intervals.items():
                # only sort real intervals
                values.sort(key=lambda l: (l[3], l[4]), reverse=False)
                labels.append(create_annoation_interval_label(values))
                for a in values:
                    labels.append(annotation_to_label(a))

            return labels


def create_noise_id_list(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_species)
            data = db_cursor.fetchall()
            return data


def export_data(
    config_path: Path = CONFIG_FILE_PATH,
    filename_labels: str = "ammod-train-single-label.csv",
    filename_class_list: str = "ammod-class-list.csv",
):
    config = parse_config(config_path)

    print("Search and create file derivations")
    derivates_dict = create_file_derivates(config)
    # multi_labels = create_multiabels(config)
    # pointing_to_derivates_multi_labels = list(
    #     map(
    #         lambda x: [x[0], x[1], x[2], x[3], x[4], derivates_dict[x[5]].as_posix()],
    #         multi_labels,
    #     )
    # )
    # write_to_csv(pointing_to_derivates_multi_labels, "ammod-train-multi-label.csv")
    single_labels = create_labels(config)
    print("Create annoation file")
    pointing_to_derivates_single_labels = list(
        filter(
            lambda x: x[1] is not None,
            list(
                map(
                    lambda x: map_filename_to_derivative_filepath(x, 1, derivates_dict),
                    single_labels,
                )
            ),
        )
    )

    write_to_csv(
        pointing_to_derivates_single_labels,
        filename_labels,
        [
            "file_id",
            "filepath",
            "channel_count",
            "collection_id",
            "class_id",
            "start_time",
            "end_time",
            "original_filename",
        ],
    )
    noise_id_list = create_noise_id_list(config)
    write_to_csv(
        noise_id_list,
        filename_class_list,
        ["latin_name", "english_name", "german_name"],
    )


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--filename-labels",
    metavar="string",
    type=str,
    nargs="?",
    default="ARSU22-WS-absent.csv",
    help="target filename for label csv",
)
parser.add_argument(
    "--filename-class-list",
    metavar="string",
    type=str,
    nargs="?",
    default="devise-class-list.csv",
    help="target filename for label csv",
)
parser.add_argument(
    "--config",
    metavar="path",
    type=Path,
    nargs="?",
    default=CONFIG_FILE_PATH,
    help="config file with database credentials",
)
args = parser.parse_args()
if __name__ == "__main__":
    export_data(
        config_path=args.config,
        filename_labels=args.filename_labels,
        filename_class_list=args.filename_class_list,
    )
