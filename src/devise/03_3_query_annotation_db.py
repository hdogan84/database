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

'''

db_connection = connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='Password123!?',
    database='libro_animalis',
    auth_plugin='mysql_native_password',
)

def query_test():

    with db_connection.cursor(dictionary=True) as db_cursor:

        # Get ARSU/Tim annotations (annotator_id = 6192)
        query = "SELECT * FROM libro_animalis.annotation_view WHERE collection LIKE '%devise%' AND annotator LIKE 'Steinkamp%';"
        #query = "SELECT * FROM libro_animalis.annotation_of_species WHERE annotator_id = 6192;"
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        print('n_rows', db_cursor.rowcount)
        for row in rows: 
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

#query_test()

def query_annotation_full_view():

    with db_connection.cursor(dictionary=True) as db_cursor:

        query = "SELECT "
        query += "a.id AS id,"
        query += "a.start_time AS start_time,"
        query += "a.end_time AS end_time,"
        query += "a.start_frequency AS start_frequency,"
        query += "a.end_frequency AS end_frequency,"
        query += "a.channel_ix AS channel_ix,"
        query += "a.vocalization_type AS vocalization_type,"
        query += "a.quality_tag AS quality_tag,"
        query += "a.id_level AS id_level,"
        query += "a.xeno_canto_background AS xeno_canto_background,"
        query += "a.created AS created,"
        query += "a.modified AS modified,"
        query += "r.original_filename AS original_filename,"
        query += "r.file_path AS file_path,"
        query += "r.filename AS filename,"
        query += "r.duration AS duration,"
        query += "r.channels AS channels,"
        query += "r.date AS date,"
        query += "r.time AS time,"
        query += "l.name AS location,"
        query += "c.name AS collection,"
        query += "s.latin_name AS latin_name,"
        query += "s.german_name AS german_name,"
        query += "s.olaf8_id AS olaf8_id,"
        query += "p.name AS annotator "
        
        query += "FROM libro_animalis.annotation_of_species a "
        query += "LEFT JOIN libro_animalis.record r ON a.record_id = r.id "
        query += "LEFT JOIN libro_animalis.species s ON a.species_id = s.id "
        query += "LEFT JOIN libro_animalis.person p ON a.annotator_id = p.id "
        query += "LEFT JOIN libro_animalis.location l ON r.location_id = l.id "
        query += "LEFT JOIN libro_animalis.collection c ON r.collection_id = c.id "

        query += "WHERE "
        query += "c.name LIKE '%devise%' "
        query += "AND a.id >= '3947823' AND a.id <= '3947935' "
        #query += "AND p.name' "


        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        n_rows = db_cursor.rowcount
        
        for row in rows:
            #print(row['id'], row['start_time']) 
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

        print('n_rows', n_rows)


#query_annotation_full_view()


print('Done.')