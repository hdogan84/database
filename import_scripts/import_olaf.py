import yaml
from os.path import exists
import mysql.connector
from tools.file_handling import get_record_annoation_tupels


DATA_PATH = "database/data/BD_Background"
CONFIG_FILE_PATH = "database/import_scripts/defaultConfig.yaml"

CONFIG = None
with open(CONFIG_FILE_PATH, "r") as stream:
    CONFIG = yaml.safe_load(stream)
if exists(DATA_PATH):
    raise FileNotFoundError(DATA_PATH)
list_of_data = get_record_annoation_tupels(DATA_PATH)
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="bewr",
#     passwd="2die3!2Die3",py
#     database="libro_cantus",
#     auth_plugin="mysql_native_password",
# )

# extract list of audio files
print(list_of_data)
