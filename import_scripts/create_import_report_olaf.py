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

DATA_PATH = Path("libro_animalis/data/TD_Training")
CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")
RECORD_MERGE_STRATEGY = "merge"


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


def create_metrics(
    data_path=DATA_PATH, report_path=Path("./"), config_path=CONFIG_FILE_PATH
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
        report_path.joinpath("merged_raven_annoations.csv"),
        sep="\t",
    )

    annotated_segments = len(all_data[all_data["SpeciesCode"] == "TD_Start_End"])
    sound_signals_total = all_data.query(
        'SpeciesCode != "TD_Start_End" & SpeciesCode != "BACKGROUND" '
    ).SpeciesCode.count()

    info("Start queriny database")
    with connectToDB(config.database) as db_connection:
        # start import files
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            db_cursor.execute(
                """
            SELECT
                latin_name, COUNT(*) AS id_level_1
            FROM (annotation_of_species AS a)
                LEFT JOIN (record AS r) ON r.id = a.record_id
                LEFT JOIN species AS s ON s.id = a.species_id
            WHERE r.collection_id = 3 and  a.id_level = 1
            GROUP BY a.species_id
            order by `id_level_1` DESC
            """
            )
            id_level_count = list(db_cursor.fetchall())

            db_cursor.execute(
                """
            SELECT
            latin_name, vocalization_type, COUNT(*) AS count
            FROM (annotation_of_species AS a)
                LEFT JOIN (record AS r) ON r.id = a.record_id
                LEFT JOIN species AS s ON s.id = a.species_id
            WHERE r.collection_id = 3 and  a.id_level = 1 
            GROUP BY a.species_id, a.vocalization_type
            order by `latin_name`,vocalization_type DESC
            """
            )
            vocalization_type_count = list(db_cursor.fetchall())
            db_cursor.execute(
                """
            SELECT sum(end_time-start_time) as duration 
            FROM libro_animalis.annotation_of_species where id_level = 1
            """
            )

            length_of_id_level_1_annoations = list(db_cursor.fetchall())[0][0]
            db_cursor.execute(
                """
            SELECT count(*) 
            FROM libro_animalis.annotation_of_species where id_level = 1
            """
            )

            level_1_annoations_count = list(db_cursor.fetchall())[0][0]

            list_to_csv(
                id_level_count,
                report_path.joinpath("id_level_count.csv"),
                ["latin_name", "count"],
            )
            list_to_csv(
                vocalization_type_count,
                report_path.joinpath("vocalization_type_count.csv"),
                ["latin_name", "vocalization_type", "count"],
            )

            # print(annotated_segments)
            # print(sound_signals_total)
            # print(level_1_annoations_count)
            # print(length_of_id_level_1_annoations)
            lines = [
                ("annotated_segments", annotated_segments),
                ("sound_signals_total", sound_signals_total),
                ("level_1_annoations_count", level_1_annoations_count),
                ("length_of_id_level_1_annoations", length_of_id_level_1_annoations),
            ]
            with open("metrics.txt", "a") as text_file:
                for line in lines:
                    text_file.write("{}: {}\n".format(line[0], line[1]))

    # print("End")


if __name__ == "__main__":
    create_metrics()