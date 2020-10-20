from pathlib import Path
from mysql.connector import connect
from tools.file_handling.collect import get_record_annoation_tupels_from_directory
from tools.file_handling.name import parse_file_name_for_location_date_time
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_get_ids_from_record_informations
from tools.file_handling.annotation import read_raven_file

DATA_PATH = Path("database/data/BD_Background")
CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

if CONFIG_FILE_PATH.exists() is False:
    raise FileNotFoundError(CONFIG_FILE_PATH)
if DATA_PATH.is_dir() is False:
    raise FileNotFoundError(DATA_PATH)

config = parse_config(CONFIG_FILE_PATH)
list_of_files = get_record_annoation_tupels_from_directory(
    DATA_PATH,
    record_file_ending=config.files.record_file_ending,
    annoation_file_ending=config.files.annoation_file_ending,
)

# check if all filenames are valid
for corresponding_files in list_of_files:
    _ = parse_file_name_for_location_date_time(corresponding_files.audio_file.stem)
    print(read_parameters_from_audio_file(corresponding_files.audio_file))
    read_raven_file(corresponding_files.annoation_file)

with connect(
    host=config.database.host,
    port=config.database.port,
    user=config.database.user,
    passwd=config.database.password,
    database=config.database.name,
    auth_plugin="mysql_native_password",
) as mySqlConnection:
    record_information_ids = check_get_ids_from_record_informations(
        mySqlConnection, config.record_information
    )
