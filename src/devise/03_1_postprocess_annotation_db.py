# conda install -c anaconda openpyxl

import os
import numpy as np
import pandas as pd
import soundfile as sf

from mysql.connector import connect, MySQLConnection

root_dir = '/mnt/z/Projekte/DeViSe/'
metadata_dir = root_dir + 'Annotationen/'

'''
ToDo's
- Correct start/end_frequency for ARSU/Tim Waldschnepfe annotationes
    # Correct start/end freq (Tim only annotated time intervals!)
    df.loc[df['vocalization_type'] == 'grunt', 'start_frequency'] = 200.0
    df.loc[df['vocalization_type'] == 'grunt', 'end_frequency'] = 2500.0 # 2000/2500
    df.loc[df['vocalization_type'] == 'squeak', 'start_frequency'] = 1500.0 # 1500/2000
    df.loc[df['vocalization_type'] == 'squeak', 'end_frequency'] = None # 24000.0/NF/None

- Link xeno-canto-annotated records to record_xeno_canto_link
- Remove xeno-canto annotationes that are part of xeno-canto-annotated

'''

db_connection = connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='Password123!?',
    database='libro_animalis',
    auth_plugin='mysql_native_password',
)

def correctTimAnnotationFrequencies():

    with db_connection.cursor(dictionary=True) as db_cursor:

        # # Update grunts
        # query = "UPDATE libro_animalis.annotation_of_species SET start_frequency=200.0, end_frequency=2500.0 WHERE annotator_id=6192 AND vocalization_type='grunt';"
        # db_cursor.execute(query)
        # db_connection.commit()

        # # Update squeak
        # query = "UPDATE libro_animalis.annotation_of_species SET start_frequency=1500.0, end_frequency=NULL WHERE annotator_id=6192 AND vocalization_type='squeak';"
        # db_cursor.execute(query)
        # db_connection.commit()

        # Get ARSU/Tim annotations (annotator_id = 6192)
        #query = "SELECT * FROM libro_animalis.annotation_view WHERE collection LIKE '%devise%' AND annotator LIKE 'Steinkamp%';"
        query = "SELECT * FROM libro_animalis.annotation_of_species WHERE annotator_id = 6192;"
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        print('n_rows', db_cursor.rowcount)
        for row in rows: 
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

#correctTimAnnotationFrequencies()

def correctLarsVocalizationType():
    
    # vocalization_type=s --> vocalization_type=song
    with db_connection.cursor(dictionary=True) as db_cursor:
        query = "UPDATE libro_animalis.annotation_of_species SET vocalization_type='song' WHERE annotator_id=6193 AND vocalization_type='s';"
        db_cursor.execute(query)
        db_connection.commit()

#correctLarsVocalizationType()

def correctChannelIxForWellenberge():
    with db_connection.cursor(dictionary=True) as db_cursor:
        query = "UPDATE `libro_animalis`.`annotation_of_species` SET `channel_ix` = NULL WHERE id >= '3947823' AND id <= '3947935';"
        db_cursor.execute(query)
        db_connection.commit()
    with db_connection.cursor(dictionary=True) as db_cursor:
        query = "UPDATE `libro_animalis`.`annotation_of_noise` SET `channel_ix` = NULL WHERE id >= '37191' AND id <= '37207';"
        db_cursor.execute(query)
        db_connection.commit()

#correctChannelIxForWellenberge()

def correctCollectionIdForArsu2022ScolopaxRusticolaAbsentFiles():
    with db_connection.cursor(dictionary=True) as db_cursor:
        query = "UPDATE `libro_animalis`.`record` SET `collection_id` = 176 WHERE id >= '1114883' AND id <= '1115680';"
        db_cursor.execute(query)
        db_connection.commit()

#correctCollectionIdForArsu2022ScolopaxRusticolaAbsentFiles()


print('Done.')