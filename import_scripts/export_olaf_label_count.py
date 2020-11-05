from mysql.connector.cursor import MySQLCursor
from pathlib import Path
import pandas as pd
from tools.configuration import parse_config
from tools.db import (
    connectToDB,
)
import csv

XLSX_FILE_PATH = "AMMOD_AV_20201023_CNN_Training_v4.xlsx"
CONFIG_FILE_PATH = Path("import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)

query = """
SELECT species.olaf8_id,
    species.latin_name,
    species.german_name,
    count(*) as label_count
from annotation_of_species a
    LEFT JOIN species on a.species_id = species.id
GROUP BY a.species_id
ORDER BY label_count DESC
"""

with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor: MySQLCursor
        db_cursor.execute(query)
        data = db_cursor.fetchall()

        with open("./ammod_labels_count.csv", "w") as out:
            csv_out = csv.writer(out)
            csv_out.writerow(
                ["Olaf8_ID", "Lateinischer Name", "Deutscher Name", "Anzahl"]
            )
            for row in data:
                csv_out.writerow(row)
