from pathlib import Path
from typing import Dict, List
from math import ceil
from datetime import timedelta
from mysql.connector.cursor import MySQLCursor
from tools.db.queries import get_id_of_entry_in_table
from tools.file_handling.collect import (
    get_record_annoation_tupels_from_directory,
    rename_and_copy_to,
)
from tools.file_handling.name import parse_filename_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file
from tools.db import (
    get_entry_id_or_create_it,
    connectToDB,
    delete_from_table,
)
from tools.logging import info
import argparse

DATA_PATH = Path("libro_animalis/data/TD_Training")
CONFIG_FILE_PATH = Path("libro_animalis/import_scripts/defaultConfig.cfg")
annotation_interval = "annotation_interval"

RECORD_MERGE_STRATEGY = "merge"
ANNOTATION_STRATEGY = "merge"
ANNOTATION_TABLE = "species"
LICENSE = None


def import_data(data_path=None, config_file_path=None) -> List[str]:
    config = parse_config(config_file_path)
    list_of_files = get_record_annoation_tupels_from_directory(
        data_path,
        record_file_ending=config.files.record_file_ending,
        annoation_file_ending=config.files.annoation_file_ending,
    )

    # check if all filenames are valid
    info("Start checking files")
    for corresponding_files in list_of_files:
        _ = parse_filename_for_location_date_time(corresponding_files.audio_file.stem)
        read_parameters_from_audio_file(corresponding_files.audio_file)
        read_raven_file(corresponding_files.annoation_file)

    info("Start importing files")
    with connectToDB(config.database) as db_connection:
        import_meta_ids = check_get_ids_from_record_informations(
            db_connection, config.record_information
        )
        # start import files
        with db_connection.cursor() as db_cursor:
            db_cursor: MySQLCursor
            failed_annotations = []
            collection_entry = [
                ("name", config.record_information.collection),
                ("remarks", None),
            ]
            collection_id = get_entry_id_or_create_it(
                db_cursor, "collection", collection_entry, collection_entry
            )
            for corresponding_files in list_of_files:

                file_name_infos = parse_filename_for_location_date_time(
                    corresponding_files.audio_file.stem
                )
                file_parameters = read_parameters_from_audio_file(
                    corresponding_files.audio_file
                )
                target_record_file_path = "{}/{}/{}".format(
                    file_parameters.md5sum[0],
                    file_parameters.md5sum[1],
                    file_parameters.md5sum[2],
                )
                record_data = [
                    ("date", file_name_infos.record_datetime.strftime("%Y-%m-%d")),
                    ("start", file_name_infos.record_datetime.time()),
                    (
                        "end",
                        (
                            file_name_infos.record_datetime
                            + timedelta(seconds=ceil(file_parameters.duration))
                        ).time(),
                    ),
                    ("duration", file_parameters.duration,),
                    ("sample_rate", file_parameters.sample_rate),
                    ("bit_depth", file_parameters.bit_depth),
                    ("bit_rate", file_parameters.bit_rate),
                    ("channels", file_parameters.channels),
                    ("mime_type", file_parameters.mime_type),
                    ("original_filename", file_parameters.original_filename),
                    ("filename", file_parameters.filename),
                    ("file_path", target_record_file_path),
                    ("md5sum", file_parameters.md5sum),
                    ("location_id", import_meta_ids.location_id),
                    ("recordist_id", import_meta_ids.recordist_id),
                    ("equipment_id", import_meta_ids.equipment_id),
                    ("collection_id", collection_id),
                    ("license", LICENSE),
                ]
                (record_id, created) = get_entry_id_or_create_it(
                    db_cursor,
                    "record",
                    [("md5sum", file_parameters.md5sum)],
                    data=record_data,
                    info=True,
                )

                db_connection.commit()
                if created:
                    targetDirectory = config.database.get_originals_files_path().joinpath(
                        target_record_file_path
                    )
                    targetDirectory.mkdir(parents=True, exist_ok=True)
                    rename_and_copy_to(
                        corresponding_files.audio_file,
                        targetDirectory,
                        file_parameters.filename,
                    )
                # remove old annotation_intervals
                delete_from_table(
                    db_cursor, "annotation_interval", [("record_id", record_id)]
                )
                db_connection.commit()
                # remove all old annotations
                delete_from_table(
                    db_cursor, "annotation_of_species", [("record_id", record_id)]
                )
                db_connection.commit()

                annotations = read_raven_file(corresponding_files.annoation_file)

                interval_id = None
                for a in annotations:
                    if a.species_code == "TD_Start_End":
                        interval_data = [
                            ("record_id", record_id),
                            ("start_time", a.start_time),
                            ("end_time", a.end_time),
                        ]

                        interval_id = get_entry_id_or_create_it(
                            db_cursor,
                            "annotation_interval",
                            query=interval_data,
                            data=interval_data,
                        )

                    species_id = get_id_of_entry_in_table(
                        db_cursor, "species", [("olaf8_id", a.species_code)]
                    )
                    if species_id is None:
                        failed_annotations.append(
                            (a.species_code, file_parameters.original_filename)
                        )
                        continue

                    annoation_data = [
                        ("record_id", record_id),
                        ("species_id", species_id),
                        ("individual_id", a.individual_id),
                        ("group_id", a.group_id),
                        ("vocalization_type", a.vocalization_type),
                        ("quality_tag", a.quality_tag),
                        ("id_level", a.id_level),
                        ("channel", a.channel),
                        ("start_time", a.start_time),
                        ("end_time", a.end_time),
                        ("start_frequency", a.start_frequency),
                        ("end_frequency", a.end_frequency),
                        ("annotator_id", import_meta_ids.annotator_id),
                        ("annotation_interval_id", interval_id),
                    ]

                    get_entry_id_or_create_it(
                        db_cursor,
                        "annotation_of_species",
                        query=annoation_data,
                        data=annoation_data,
                    )
                db_connection.commit()

            # to distinct species values
            labels = {}
            for fa in failed_annotations:
                if fa[0] not in labels:
                    labels.update({fa[0]: "\t" + fa[1]})
                else:
                    labels.update({fa[0]: labels.get(fa[0]) + "\n \t" + fa[1]})

            # for x in labels:
            #     print(x)
            # print(labels[x])

            info(
                "Failed annotations not matched species {}".format(
                    len(failed_annotations)
                )
            )
            # read_raven_file(corresponding_files.annoation_file)
            return labels


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--data",
    metavar="path",
    type=Path,
    nargs="?",
    help="target folder",
    default=DATA_PATH,
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
    import_data(args.data, args.config)
