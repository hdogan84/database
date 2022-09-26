from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from import_scripts.import_annoations_olaf import ANNOTATION_STRATEGY
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from derivates import Standart32khz as Derivative
import argparse
from tools.file_handling.csv import write_to_csv
from enum import Enum, IntEnum
from export_scripts.export_tools import map_filename_to_derivative_filepath

COLLECTION_ID = 176
BACKGROUND_LEVEL = ""
SET_FILENAME = "devise-test-2.csv"
CLASS_LIST_FILENAME = "devise-class-list.csv"
CONFIG_FILE_PATH = Path("config_training.cfg")
class_list = """ 
(
'AVSCSCRU'
)
"""
#'AVRACRCR',

query_files = """
SELECT 
    distinct(r.filename), r.file_path
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
        LEFT JOIN
    location AS l ON l.id = r.location_id
WHERE
    l.name = "Gellener Torfmöörte" and
    r.collection_id = {} and
    s.olaf8_id IN {}

""".format(
    COLLECTION_ID, class_list
)

query_annoations = """
SELECT 
    s.latin_name,
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
    a.background_level,
    a.start_frequency,
    a.end_frequency,
    l.name,
    r.id
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
        LEFT JOIN
    annotation_interval AS i ON i.id = a.annotation_interval_id 
        LEFT JOIN
    location AS l ON l.id = r.location_id 
   
WHERE
    l.name = "Gellener Torfmöörte" and
    r.collection_id = {} and
    s.olaf8_id IN {} 
   
 ORDER BY r.filename , a.start_time ASC
 """.format(
    COLLECTION_ID, class_list
)

query_species = """
SELECT latin_name,english_name,german_name FROM libro_animalis.species where
    olaf8_id IN {}
ORDER BY latin_name ASC
""".format(
    class_list
)

annotation_interval = "annotation_interval"


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
    BACKGROUND_LEVEL = 15
    START_FREQ = 16
    END_FREQ = 17
    LOCATION = 18


def create_file_derivates(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_files)
            data = db_cursor.fetchall()
            filepathes = list(map(lambda x: (Path(x[1]).joinpath(x[0])), data))
            derivatateCreator = Derivative(config.database)
            file_derivates_dict = derivatateCreator.get_original_derivate_dict(
                filepathes
            )
            return file_derivates_dict


def annotation_to_label(annotation):
    # print(annotation)
    collection_id = annotation[Index.COLLECTION_ID]
    channels = annotation[Index.CHANNELS]
    duration = annotation[Index.END_TIME] - annotation[Index.START_TIME]
    start = annotation[Index.START_TIME]
    stop = annotation[Index.END_TIME]
    label = annotation[Index.LATIN_NAME]
    filename = "derivation/1/" + annotation[1] + "/" + annotation[Index.FILENAME]
    calltype = annotation[Index.VOCALIZATION_TYPE]
    quality = annotation[Index.QUALITY_TAG]
    background_level = annotation[Index.BACKGROUND_LEVEL]
    start_frequency = annotation[Index.START_FREQ]
    end_frequency = annotation[Index.END_FREQ]
    location = annotation[Index.LOCATION]
    # return (duration, start, stop, label, 1, filename, channels, collection_id)
    return (
        Path(filename).stem,
        filename,
        channels,
        collection_id,
        label,
        start,
        stop,
        calltype,
        quality,
        background_level,
        start_frequency,
        end_frequency,
        location,
    )


def create_annoation_interval_label(row, annotation_list):
    # take first element in list to estimate annoation interval start
    annotation = annotation_list[0]
    collection_id = annotation[Index.COLLECTION_ID]
    channels = annotation[Index.CHANNELS]
    duration = annotation[Index.DURATION]
    start = 0

    stop = annotation[Index.DURATION]

    label = "annotation_interval"
    filename = "derivation/1/" + annotation[1] + "/" + annotation[Index.FILENAME]
    return (
        Path(filename).stem,
        filename,
        channels,
        collection_id,
        label,
        start,
        stop,
    )


def create_labels(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_annoations)
            data = db_cursor.fetchall()
            print("Found {} annotations".format(len(data)))
            # print(data[0])
            # print(data[50])
            # return

            labels = []
            intervals = {}
            # Collect Labels of Different record intervalls
            for a in data:
                if a[12] is None:
                    if str(a[19]) in intervals:

                        intervals[str(a[19])].append(a)
                    else:
                        intervals.update({str(a[19]): [a]})
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
            # print(intervals)

            for key, values in intervals.items():
                # only sort real intervals
                values.sort(key=lambda l: (l[3], l[4]), reverse=False)
                labels.append(create_annoation_interval_label(a[1], values))

                for a in values:
                    labels.append(annotation_to_label(a))

            return labels


def create_class_list(config: DatabaseConfig):
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

    print("Search an create file derivations")
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
    print(single_labels[0])
    print(single_labels[1])
    print(single_labels[2])

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
            "start_frequency",
            "end_frequency",
            "vocalization_type",
            "quality_tag",
            "background_level",
            "location",
        ],
    )
    class_list = create_class_list(config)
    write_to_csv(
        class_list, filename_class_list, ["latin_name", "english_name", "german_name"]
    )


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--filename-labels",
    metavar="string",
    type=str,
    nargs="?",
    default=SET_FILENAME,
    help="target filename for label csv",
)
parser.add_argument(
    "--filename-class-list",
    metavar="string",
    type=str,
    nargs="?",
    default=CLASS_LIST_FILENAME,
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
