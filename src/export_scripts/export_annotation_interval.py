from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from import_scripts.import_annoations_olaf import ANNOTATION_STRATEGY
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from derivates import Standart32khz
import argparse
from tools.file_handling.csv import write_to_csv
from enum import Enum, IntEnum
from export_scripts.export_tools import map_filename_to_derivative_filepath

CONFIG_FILE_PATH = Path("config_training.cfg")
class_list = """
(
'AVRACRCR',
'AVSCSCRU',
'AVPIDEMA',
'AVPDPEAT',
'AVPDLOCR',
'AVPDPOPA',
'AVPDCYCA',
'AVPDPAMA',
'AVPCPHSI',
'AVPCPHTR',
'AVSYSYAT',
'AVTGTRTR',
'AVSISIEU',
'AVTUTUME',
'AVTUTUPH',
'AVTUTUVI',
'AVMUMUST',
'AVMUERRU',
'AVMUFIHY',
'AVMUPHPH',
'AVMTANTR',
'AVFRFRCO',
'AVFRCOCO',
'AVFRCHCH',
'AVFRSPSP')
"""
query_files = """
SELECT 
    distinct(r.filename), r.file_path
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
WHERE
    a.background = 0 and
    r.collection_id != 105 and
    s.olaf8_id IN {}

""".format(
    class_list
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
    r.`channels`,
    r.collection_id,
    r.duration,
    i.id,
    i.start_time,
    i.end_time
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
        LEFT JOIN
    annotation_interval AS i ON i.id = a.annotation_interval_id 
WHERE
    a.background = 0 and
    r.collection_id != 105 and
    s.olaf8_id IN {}
ORDER BY r.filename , a.start_time ASC
""".format(
    class_list
)

query_species = """
SELECT latin_name,english_name,german_name FROM libro_animalis.species where
    olaf8_id IN {}
ORDER BY latin_name ASC
""".format(
    class_list
)

TD_START_END = "TD_Start_End"


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


def create_file_derivates(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_files)
            data = db_cursor.fetchall()
            filepathes = list(map(lambda x: (Path(x[1]).joinpath(x[0])), data))
            derivatateCreator = Standart32khz(config.database)
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
    return (duration, start, stop, label, 1, filename, channels, collection_id)


def create_td_start_label(annotation_list):
    # take first element in list to estimate annoation interval start
    annotation = annotation_list[0]
    collection_id = annotation[Index.COLLECTION_ID]
    channels = annotation[Index.CHANNELS]
    duration = annotation[Index.DURATION]
    start = (
        annotation[Index.ANNOTATION_INTERVAL_START]
        if annotation[Index.ANNOTATION_INTERVAL_ID] is not None
        else annotation[Index.START_TIME]
    )
    stop = (
        annotation[Index.ANNOTATION_INTERVAL_END]
        if annotation[Index.ANNOTATION_INTERVAL_ID] is not None
        else annotation[Index.DURATION]
    )
    label = TD_START_END
    filename = annotation[Index.FILENAME]
    return (duration, start, stop, label, 1, filename, channels, collection_id)


def create_labels(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_annoations)
            data = db_cursor.fetchall()
            print("Found {} annotations".format(len(data)))

            labels = []
            intervals = {"None": []}
            # Collect Labels of Different record intervalls
            for a in data:
                if a[12] is None:
                    intervals["None"].append(a)
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
                if key is not "None":
                    values.sort(key=lambda l: (l[3], l[4]), reverse=False)
                    labels.append(create_td_start_label(values))
                    for a in values:
                        labels.append(annotation_to_label(a))
                else:
                    for a in values:
                        labels.append(create_td_start_label([a]))
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
    print("Create annoation file")
    pointing_to_derivates_single_labels = list(
        filter(
            lambda x: x[5] is not None,
            list(
                map(
                    lambda x: map_filename_to_derivative_filepath(x, 5, derivates_dict),
                    single_labels,
                )
            ),
        )
    )
    # filter file length
    # pointing_to_derivates_single_labels = list(
    #     filter(lambda x: x[0] < 120 and x[0] > 0.2, pointing_to_derivates_single_labels)
    # )
    write_to_csv(
        pointing_to_derivates_single_labels,
        filename_labels,
        [
            "duration",
            "start_time",
            "end_time",
            "labels",
            "species_count",
            "filepath",
            "channels",
            "collection_id",
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
    default="ammod-labels.csv",
    help="target filename for label csv",
)
parser.add_argument(
    "--filename-class-list",
    metavar="string",
    type=str,
    nargs="?",
    default="ammod-class-list.csv",
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
