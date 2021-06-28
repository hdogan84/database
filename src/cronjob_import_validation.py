#!/home/tsa/miniconda3/bin/python

from pathlib import Path
from import_scripts.import_annoations_olaf import import_data
from create_import_report_olaf import create_metrics
import datetime
import os

DATA_PATH = Path("/mnt/z/Projekte/AMMOD/Audioannotation/VD_Validierung")
CONFIG_FILE_PATH = Path("/home/tsa/projects/libro-animalis/config_validation.cfg")

currentDate = datetime.datetime.strptime("01/08/2015", "%d/%m/%Y").date()
missing_species = import_data(DATA_PATH, CONFIG_FILE_PATH)
now = datetime.date.today().strftime("%Y-%m-%d")

report_path = DATA_PATH.joinpath("report", now)
report_path.mkdir(parents=True, exist_ok=True)
create_metrics(
    Path(DATA_PATH),
    report_path,
    Path(CONFIG_FILE_PATH),
    missing_species=missing_species,
    collectionId=105,
)
