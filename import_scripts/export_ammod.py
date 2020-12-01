from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import derivates
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import (
    connectToDB,
)
from derivates import Standart22khz
from tools.multilabel import SimpleMultiLabels
import csv

CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)

query_files = """
SELECT 
    distinct(r.filename)
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
WHERE
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

"""

query_annoations = """
SELECT 
    s.latin_name,
	r.filename,
    a.start_time,
    a.end_time,
    a.quality_tag,
    a.individual_id,
    a.group_id,
    a.vocalization_type,
    a.`channel`
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
WHERE
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


def create_file_derivates(config: DatabaseConfig):
    with connectToDB(config.database) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor  # set type hint
            db_cursor.execute(query_files)
            data = db_cursor.fetchall()
            filenames = list(map(lambda x: x[0], data))
            derivatateCreator = Standart22khz(config.database)
            file_derivates_dict = derivatateCreator.get_original_derivate_dict(
                filenames
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


def write_to_csv(data, filename):
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(
            csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(
            [
                "duration",
                "start_time",
                "end_time",
                "labels",
                "species_count",
                "filename",
            ]
        )
        csv_writer.writerows(data)


derivates_dict = create_file_derivates(config)
multi_labels = create_multiabels(config)
single_labels = create_singleLabels(config)
pointing_to_derivates_multi_labels = list(
    map(
        lambda x: [x[0], x[1], x[2], x[3], x[4], derivates_dict[x[5]].as_posix()],
        multi_labels,
    )
)
pointing_to_derivates_single_labels = list(
    map(
        lambda x: [x[0], x[1], x[2], x[3], x[4], derivates_dict[x[5]].as_posix()],
        single_labels,
    )
)
# csv_filename = "ammod-train-multi-label.csv"
csv_filename = "ammod-train-single-label.csv"
write_to_csv(pointing_to_derivates_multi_labels, "ammod-train-multi-label.csv")
write_to_csv(pointing_to_derivates_single_labels, "ammod-train-single-label.csv")