from typing import List, Dict
from mysql.connector.cursor import MySQLCursor
from pathlib import Path
from tools.logging import debug
from tools.configuration import parse_config
from tools.db import (
    connectToDB,
)
from derivates import Standart22khz


CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)

query_files = """
SELECT 
    distinct(r.file_name)
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
derivatateCreator = Standart22khz(config.database)

with connectToDB(config.database) as db_connection:
    with db_connection.cursor() as db_cursor:
        db_cursor: MySQLCursor
        db_cursor.execute(query_files)
        data = db_cursor.fetchall()
        file_names = list(map(lambda x: x[0], data))
        file_derivates_dict = derivatateCreator.get_original_derivate_dict(file_names)
        print(file_derivates_dict)
