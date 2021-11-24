from pathlib import Path
from typing import Dict, List
from tools.file_handling.collect import (
    CorespondingFiles,
    get_record_annoation_tupels_from_directory,
)
from pandas import read_csv, concat, DataFrame
import csv
from tools.configuration import parse_config

from mysql.connector.cursor import MySQLCursor
from tools.logging import info
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
)
from numpy import median

DATA_PATH = Path("libro_animalis/data/TD_Training")
REPORT_PATH = Path("./")
CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")
RECORD_MERGE_STRATEGY = "replace"

QUERY_RECORD_COUNT = """
            SELECT COUNT(*) FROM libro_animalis.record where collection_id = {collection_id}
            """
QUERY_RECORD_DURATION = """
            SELECT sum(r.duration) as duration FROM record AS r
                WHERE r.collection_id = {collection_id}
            """

QUERY_ID_LEVEL_COUNT = """
            SELECT
                latin_name,olaf8_id,german_name,english_name, COUNT(*) AS id_level
            FROM (annotation_of_species AS a)
                LEFT JOIN (record AS r) ON r.id = a.record_id
                LEFT JOIN species AS s ON s.id = a.species_id
            WHERE r.collection_id = {collection_id} and  a.id_level = {id_level}
            GROUP BY a.species_id
            order by `id_level` DESC
            """

QUERY_VOCALIZATIOM_TYPE_COUNT = """
            SELECT
            latin_name,olaf8_id,german_name,english_name, vocalization_type, COUNT(*) AS count
            FROM (annotation_of_species AS a)
                LEFT JOIN (record AS r) ON r.id = a.record_id
                LEFT JOIN species AS s ON s.id = a.species_id
            WHERE r.collection_id = {collection_id} and  a.id_level = {id_level} 
            GROUP BY a.species_id, a.vocalization_type
            order by `latin_name`,vocalization_type DESC
            """
QUERY_LENGTH_OF_ID_LEVEL_ANOTATIONS = """
            SELECT SUM(a.end_time - a.start_time) AS duration
            FROM libro_animalis.annotation_of_species AS a
            LEFT JOIN (record AS r) ON r.id = a.record_id
            WHERE r.collection_id = {collection_id} AND a.id_level = {id_level} 
            """

QUERY__ID_LEVEL_ANOTATIONS_COUNT = """SELECT count(*) 
            FROM libro_animalis.annotation_of_species as a
            LEFT JOIN (record AS r) ON r.id = a.record_id
            WHERE r.collection_id = {collection_id} AND
            a.id_level = {id_level} 
            """
QUERY_ANNOTATION_INTERVALL_DURATION = """
    SELECT (a.end_time - a.start_time) as duration FROM libro_animalis.annotation_interval as a
	 LEFT JOIN (record AS r) ON r.id = a.record_id
	 WHERE r.collection_id = {collection_id}
"""


def list_to_csv(data: list, file_path: Path, head_row: List[str]):
    with open(file_path, "w") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(head_row)
        for row in data:
            csv_out.writerow(row)


def add_filename(data_frame: DataFrame, filename: str) -> DataFrame:
    # data_frame.assign(filename=filename)
    data_frame["filename"] = data_frame.apply(lambda x: filename, axis=1)
    tmp = data_frame["filename"]
    data_frame.drop(labels=["filename"], axis=1, inplace=True)
    data_frame.insert(0, "filename", tmp)
    return data_frame.copy(deep=True)


def create_merged_raven_files(list_of_files: List[CorespondingFiles]):

    annotations = list(
        map(
            lambda x: add_filename(
                read_csv(
                    open(x.annoation_file, "rb"),
                    delimiter="\t",
                    encoding="unicode_escape",
                ),
                x.audio_file.name,
            ),
            list_of_files,
        ),
    )
    result = concat(annotations)
    return result


def merge_species_lists(dict, id_level_species_count_list, key):
    for entry in id_level_species_count_list:

        if entry[0] not in dict:
            dict[entry[0]] = {
                "names": list(entry[0:4]),
                key: entry[4],
            }
        else:
            dict[entry[0]][key] = entry[4]
    return dict


def create_metrics(
    data_path=None,
    report_path=None,
    config_path=None,
    missing_species=None,
    collectionId=None,
):
    config = parse_config(config_path)

    list_of_files = get_record_annoation_tupels_from_directory(
        data_path,
        record_file_ending=config.files.record_file_ending,
        annoation_file_ending=config.files.annoation_file_ending,
    )

    # check if all filenames are valid
    # info("Merging files")
    all_data = create_merged_raven_files(list_of_files)

    # write merged raven file
    all_data.to_csv(
        report_path.joinpath("merged_raven_annoations.txt"), sep="\t",
    )

    annotated_segments = len(all_data[all_data["SpeciesCode"] == "TD_Start_End"])
    sound_signals_total = all_data.query(
        'SpeciesCode != "annotation_interval" & SpeciesCode != "BACKGROUND" '
    ).SpeciesCode.count()

    info("Start querieng database")
    with connectToDB(config.database) as db_connection:
        # start import files
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            # -- id_level_1_species_count
            db_cursor.execute(
                QUERY_ID_LEVEL_COUNT.format(collection_id=collectionId, id_level=1)
            )
            id_level_1_species_count = list(db_cursor.fetchall())
            # -- id_level_2_species_count
            db_cursor.execute(
                QUERY_ID_LEVEL_COUNT.format(collection_id=collectionId, id_level=2)
            )
            id_level_2_species_count = list(db_cursor.fetchall())
            # -- id_level_3_species_count
            db_cursor.execute(
                QUERY_ID_LEVEL_COUNT.format(collection_id=collectionId, id_level=3)
            )
            id_level_3_species_count = list(db_cursor.fetchall())

            dict = merge_species_lists({}, id_level_1_species_count, "id_1")
            dict = merge_species_lists(dict, id_level_2_species_count, "id_2")
            dict = merge_species_lists(dict, id_level_3_species_count, "id_3")

            id_level_species_count = []

            for species in dict:
                id_level_species_count.append(
                    dict[species]["names"]
                    + [
                        dict[species]["id_1"] if "id_1" in dict[species] else 0,
                        dict[species]["id_2"] if "id_2" in dict[species] else 0,
                        dict[species]["id_3"] if "id_3" in dict[species] else 0,
                    ]
                )

            # -- vocalization_type_count
            db_cursor.execute(
                QUERY_VOCALIZATIOM_TYPE_COUNT.format(
                    collection_id=collectionId, id_level=1
                )
            )
            vocalization_type_count = list(db_cursor.fetchall())

            # --- length_of_id_level_1_annoations
            db_cursor.execute(
                QUERY_LENGTH_OF_ID_LEVEL_ANOTATIONS.format(
                    collection_id=collectionId, id_level=1
                )
            )
            length_of_id_level_1_annoations = list(db_cursor.fetchall())[0][0]

            # --- length_of_id_level_2_annoations
            db_cursor.execute(
                QUERY_LENGTH_OF_ID_LEVEL_ANOTATIONS.format(
                    collection_id=collectionId, id_level=2
                )
            )
            length_of_id_level_2_annoations = list(db_cursor.fetchall())[0][0]

            # -- length_of_id_level_3_annoations
            db_cursor.execute(
                QUERY_LENGTH_OF_ID_LEVEL_ANOTATIONS.format(
                    collection_id=collectionId, id_level=3
                )
            )
            length_of_id_level_3_annoations = list(db_cursor.fetchall())[0][0]

            # - level_1_annoations_count
            db_cursor.execute(
                QUERY__ID_LEVEL_ANOTATIONS_COUNT.format(
                    collection_id=collectionId, id_level=1
                )
            )
            level_1_annoations_count = list(db_cursor.fetchall())[0][0]
            # - level_2_annoations_count
            db_cursor.execute(
                QUERY__ID_LEVEL_ANOTATIONS_COUNT.format(
                    collection_id=collectionId, id_level=2
                )
            )
            level_2_annoations_count = list(db_cursor.fetchall())[0][0]
            # - level_3_annoations_count
            db_cursor.execute(
                QUERY__ID_LEVEL_ANOTATIONS_COUNT.format(
                    collection_id=collectionId, id_level=3
                )
            )
            level_3_annoations_count = list(db_cursor.fetchall())[0][0]

            # - file_count
            db_cursor.execute(QUERY_RECORD_COUNT.format(collection_id=collectionId))
            file_count = list(db_cursor.fetchall())[0][0]

            # - file_duration
            db_cursor.execute(QUERY_RECORD_DURATION.format(collection_id=collectionId))
            file_duration = list(db_cursor.fetchall())[0][0]

            # - annotation_segments
            db_cursor.execute(
                QUERY_ANNOTATION_INTERVALL_DURATION.format(collection_id=collectionId)
            )
            result = db_cursor.fetchall()

            annotated_segments_durations = (
                [x[0] for x in result] if (len(result) > 0) else [0]
            )
            annotated_segments_duration = sum(annotated_segments_durations)
            annotated_segments_max = max(annotated_segments_durations)
            annotated_segments_min = min(annotated_segments_durations)
            annotated_segments_median = median(annotated_segments_durations)

            # -- write csv files
            list_to_csv(
                id_level_species_count,
                report_path.joinpath("id_level_species_count.csv"),
                [
                    "latin_name",
                    "olaf_code",
                    "german_name",
                    "english_name",
                    "id_1",
                    "id_2",
                    "id_3",
                ],
            )
            list_to_csv(
                vocalization_type_count,
                report_path.joinpath("vocalization_type_count.csv"),
                [
                    "latin_name",
                    "olaf_code",
                    "german_name",
                    "english_name",
                    "vocalization_type",
                    "count",
                ],
            )

            # print(annotated_segments)
            # print(sound_signals_total)
            # print(level_1_annoations_count)
            # print(length_of_id_level_1_annoations)
            lines = [
                ("annotated_file_count", file_count),
                ("annotated_file_duration", file_duration),
                ("annotated_segments", annotated_segments),
                ("annotated_segments_duration", annotated_segments_duration),
                ("annotated_segments_max", annotated_segments_max),
                ("annotated_segments_min", annotated_segments_min),
                ("annotated_segments_median", annotated_segments_median),
                ("sound_signals_total", sound_signals_total),
                ("level_1_annoations_count", level_1_annoations_count),
                ("length_of_id_level_1_annoations", length_of_id_level_1_annoations),
                ("level_2_annoations_count", level_2_annoations_count),
                ("length_of_id_level_2_annoations", length_of_id_level_2_annoations),
                ("level_3_annoations_count", level_3_annoations_count),
                ("length_of_id_level_3_annoations", length_of_id_level_3_annoations),
            ]
            metrics_filepath = report_path.joinpath("metrics.txt")
            with open(metrics_filepath, "w") as text_file:
                for line in lines:
                    text_file.write("{}: {}\n".format(line[0], line[1]))
            if missing_species is not None:
                missing_species_filepath = report_path.joinpath("missing_species.txt")
                with open(missing_species_filepath, "w") as text_file:
                    text_file.writelines(list(map(lambda x: x + "\n", missing_species)))

    # print("End")


if __name__ == "__main__":
    create_metrics()
