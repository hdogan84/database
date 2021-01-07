from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import derivates
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import connectToDB
from derivates import Standart32khz
from tools.multilabel import SimpleMultiLabels
import argparse
from tools.file_handling.csv import write_to_csv

CONFIG_FILE_PATH = Path("config.cfg")

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
    r.collection_id != 1 and
    s.olaf8_id IN (
        'AVPDPEAT', 
        'AVPIDEMA',
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
    r.`channels`
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
WHERE
    r.collection_id != 1 and
    s.olaf8_id IN ('AVPDPEAT' , 'AVPIDEMA',
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
ORDER BY r.filename , a.start_time ASC
"""

query_species = """
SELECT latin_name,english_name,german_name FROM libro_animalis.species where
    olaf8_id IN ('AVPDPEAT' , 'AVPIDEMA',
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
        ORDER BY latin_name ASC
"""


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


def create_multiabels(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_annoations)
            data = db_cursor.fetchall()

            multiLableGenerator = SimpleMultiLabels(data)
            labels = multiLableGenerator.create_multi_labels()
            return labels


def create_singleLabels(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_annoations)
            data = db_cursor.fetchall()
            labelGenerator = SimpleMultiLabels(data)
            labels = labelGenerator.create_single_labels()
            return labels


def create_class_list(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_species)
            data = db_cursor.fetchall()
            return data


def map_filename_to_derivative_filepath(
    data_row: tuple, filename_index: dict, derivates_dict
):
    result = list(data_row)
    try:
        result[filename_index] = derivates_dict[result[filename_index]].as_posix()
    except KeyError as e:
        print(e)
        result[filename_index] = None
    return result


def export_data(
    config_path: Path = CONFIG_FILE_PATH,
    filename_labels: str = "ammod-train-single-label.csv",
    filename_class_list: str = "ammod-class-list.csv",
):
    config = parse_config(config_path)

    derivates_dict = create_file_derivates(config)
    # multi_labels = create_multiabels(config)
    # pointing_to_derivates_multi_labels = list(
    #     map(
    #         lambda x: [x[0], x[1], x[2], x[3], x[4], derivates_dict[x[5]].as_posix()],
    #         multi_labels,
    #     )
    # )
    # write_to_csv(pointing_to_derivates_multi_labels, "ammod-train-multi-label.csv")
    single_labels = create_singleLabels(config)
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
    default="labels.csv",
    help="target filename for label csv",
)
parser.add_argument(
    "--filename-class-list",
    metavar="string",
    type=str,
    nargs="?",
    default="class-list.csv",
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
