from pathlib import Path
from mysql.connector import connect
from tools.file_handling import get_record_annoation_tupels
from tools.configuration import parse_config
from tools.sub_scripts.record_information import check_record_information

DATA_PATH = Path("database/data/BD_Background")
CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

if CONFIG_FILE_PATH.exists() is False:
    raise FileNotFoundError(CONFIG_FILE_PATH)
if DATA_PATH.is_dir() is False:
    raise FileNotFoundError(DATA_PATH)

config = parse_config(CONFIG_FILE_PATH)
list_of_data = get_record_annoation_tupels(DATA_PATH)

with connect(
    host=config.database.host,
    port=config.database.port,
    user=config.database.user,
    passwd=config.database.password,
    database=config.database.name,
    auth_plugin="mysql_native_password",
) as mySqlConnection:
    check_record_information(mySqlConnection, config.record_information)
