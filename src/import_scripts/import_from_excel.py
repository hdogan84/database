import csv
from pathlib import Path
from tools.file_handling.collect import rename_and_copy_to
from tools.file_handling.audio import read_parameters_from_audio_file
from tools.logging import debug, info, error
from tools.db import (
    get_entry_id_or_create_it,
    get_id_of_entry_in_table,
    connectToDB,
)
from tools.logging import info
import argparse

import os
import pandas as pd
from mysql.connector import connect, MySQLConnection

ROOT_DIR = '/mnt/z/Projekte/DeViSe/'

#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_MfN_Peenemuende+Schoenow_v04.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_ARSU_2021_v06.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_ARSU_2022_v06.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Crex_crex_Unteres_Odertal_2017_v02.xlsx'

#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/CrexCrex_LarsAnnotaions_v03.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_FVA_v02.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Crex_crex_Wellenberge_Lokalisation_2017_v02.xlsx'

#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_BG_ARSU_2022_v07.xlsx'
#EXCEL_PATH = ROOT_DIR + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_BG_ARSU_2021_v07.xlsx'



audio_root_dir = '/net/mfnstore-lin/export/tsa_transfer/TrainData/libro_animalis/temp/'
#audio_root_dir = '/net/mfnstore-lin/export/tsa_transfer/TrainData/libro_animalis/original/'

allow_noise_name_insert = True

db_connection = connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='Password123!?',
    database='libro_animalis',
    auth_plugin='mysql_native_password',
)

keys = [
    'filename',
    'start_time',
    'end_time',
    'start_frequency',
    'end_frequency',
    'channel_ix',
    'individual_id',
    'group_id',
    'vocalization_type',
    'quality_tag',
    'id_level',
    'background_level',         # 0 none; 1 little; 2 a lot;
    'xeno_canto_background',    # Only for xeno_canto files if species is annotated as background species
    'species_latin_name',       # if species_latin_name --> insert in annotation_of_species
    'noise_name',               # if noise_name --> insert in annotation_of_noise
    'remarks',
    'annotator_name',
    'annotation_interval_start',
    'annotation_interval_end',
    'record_date',
    'record_time',              # record_start --> record_time
    'record_end',               # Maybe remove
    'record_filepath',
    'record_license',
    'record_remarks',
    'recordist_name',
    'equipment_name',
    'equipment_sound_device',
    'equipment_microphone',
    'equipment_remarks',
    'location_name',
    'location_description',
    'location_habitat',
    'location_lat',
    'location_lng',
    'location_altitude',
    'location_remarks',
    'collection_name',
    'collection_remarks'
]


# Init values with data or assign None
def get_values(keys, input_dict):
    output_dict = {}
    for key in keys:
        output_dict[key] = None
        # Empty string is interpreted as None
        if key in input_dict and (input_dict[key] or input_dict[key] == 0 or input_dict[key] == 0.0): 
            output_dict[key] = input_dict[key]
    return output_dict


def import_from_excel(path, dry_run=False):

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    # Read excel file to dataframe
    df = pd.read_excel(path, keep_default_na=False, engine='openpyxl')
    cols = list(df.columns)
    print(df)
    print(cols)
    print('n_rows', len(df))

    # Store audio file parameters per filepath
    audio_file_parameters_dict = {}

    # ToDo maybe check and remove cols without any data


    with db_connection.cursor(dictionary=False) as db_cursor:

        # # Test db via query
        # db_cursor.execute('SELECT * FROM libro_animalis.annotation_view LIMIT 4;')
        # myresult = db_cursor.fetchall()
        # for x in myresult: print(x)

        # Iterate over rows
        for ix, row in df.iterrows():

            # Test only a few
            #if ix > 15: break

            # Preprocess values (return None if column not present or input is empty/NaN)
            val = get_values(keys, row)

            # Get collection_id or create it and insert collection data
            collection_id = None
            collection_entry = [('name', val['collection_name']), ('remarks', val['collection_remarks'])]
            collection_id = get_entry_id_or_create_it(db_cursor, 'collection', collection_entry, collection_entry)
            #print('collection_id', collection_id, 'collection_remarks', val['collection_remarks'])

            
            # Get recordist_id or create it and insert person data
            recordist_id = None
            if val['recordist_name']:
                recordist_entry = [('name', val['recordist_name'])]
                recordist_id = get_entry_id_or_create_it(db_cursor, 'person', recordist_entry, recordist_entry)
            #print('recordist_id', recordist_id, 'recordist_name', val['recordist_name'])


            # Get equipment_id or create it and insert equipment data
            equipment_id = None
            if val['equipment_name']:
                equipment_entry = [
                    ('name', val['equipment_name']),
                    ('sound_device', val['equipment_sound_device']),
                    ('microphone', val['equipment_microphone']),
                    ('remarks', val['equipment_remarks']),
                    ]
                equipment_id = get_entry_id_or_create_it(db_cursor, 'equipment', equipment_entry, equipment_entry)
            #print('equipment_id', equipment_id, 'equipment_name', val['equipment_name'])


            # Get location_id or create it and insert location data
            location_id = None
            if val['location_name']:
                location_entry = [
                    ('name', val['location_name']),
                    ('description', val['location_description']),
                    ('habitat', val['location_habitat']),
                    ('lat', val['location_lat']),
                    ('lng', val['location_lng']),
                    ('altitude', val['location_altitude']),
                    ('remarks', val['location_remarks']),
                    ]
                location_id = get_entry_id_or_create_it(db_cursor, 'location', location_entry, location_entry)
            #print('location_id', location_id, 'location_name', val['location_name'])

            
            # Get annotator_id or create it and insert person data
            annotator_id = None
            if val['annotator_name']:
                annotator_entry = [('name', val['annotator_name'])]
                annotator_id = get_entry_id_or_create_it(db_cursor, 'person', annotator_entry, annotator_entry)
            #print('annotator_id', annotator_id, 'annotator_name', val['annotator_name'])


            # Get species_id (insert currently not allowed)
            species_id = None
            if val['species_latin_name']:
                species_entry = [('latin_name', val['species_latin_name'])]
                #species_id = get_entry_id_or_create_it(db_cursor, 'species', species_entry, species_entry)
                species_id = get_id_of_entry_in_table(db_cursor, 'species', species_entry)
            #print('species_id', species_id, 'species_latin_name', val['species_latin_name'])

            if val['species_latin_name'] and not species_id:
                print('Species name not found in db', val['species_latin_name'])

            # Get noise_id or create it (insert currently not allowed)
            noise_id = None
            if val['noise_name']:
                noise_entry = [('name', val['noise_name'])]
                if allow_noise_name_insert:
                    noise_id = get_entry_id_or_create_it(db_cursor, 'noise', noise_entry, noise_entry)
                else:
                    noise_id = get_id_of_entry_in_table(db_cursor, 'noise', noise_entry)

            if not species_id and not noise_id:
                print('Noise name not found in db', val['noise_name'])



            filepath = Path(row['record_filepath'])
            filepath_str = filepath.as_posix()

            if not filepath.exists():
                error('File does not exhist {}'.format(filepath_str))
                continue
            
            if filepath_str not in audio_file_parameters_dict:
                #audio_file_parameters = None
                try:
                    audio_file_parameters = read_parameters_from_audio_file(filepath)
                    audio_file_parameters_dict[filepath_str] = audio_file_parameters
                except:
                    error('Could not read audio Parameters from {}'.format(filepath_str))
                    continue
            else:
                audio_file_parameters = audio_file_parameters_dict[filepath_str]


            target_record_file_path = '{}/{}/{}'.format(
                audio_file_parameters.md5sum[0],
                audio_file_parameters.md5sum[1],
                audio_file_parameters.md5sum[2],
            )


            # Add recording infos
            record_entry = [
                ('duration', audio_file_parameters.duration),
                ('sample_rate', audio_file_parameters.sample_rate),
                ('bit_depth', audio_file_parameters.bit_depth),
                ('bit_rate', audio_file_parameters.bit_rate),
                ('channels', audio_file_parameters.channels),
                ('mime_type', audio_file_parameters.mime_type),
                ('original_filename', audio_file_parameters.original_filename,),
                ('file_path', target_record_file_path),
                ('filename', audio_file_parameters.filename),
                ('md5sum', audio_file_parameters.md5sum),
                
                ('date', val['record_date']),
                ('time', val['record_time']),
                ('end', None),
                ('license', val['record_license']),
                ('remarks',val['record_remarks']),

                ('collection_id', collection_id),
                ('recordist_id', recordist_id),
                ('equipment_id', equipment_id),
                ('location_id', location_id),
            ]

            # Get record_id or create it and insert recording data
            (record_id, record_created) = get_entry_id_or_create_it(
                db_cursor,
                'record',
                [('md5sum', audio_file_parameters.md5sum),],
                data=record_entry,
                info=True,
            )


            if record_created:
                # move file to destination
                if dry_run is False:
                    #targetDirectory = config.database.get_originals_files_path().joinpath(target_record_file_path)
                    targetDirectory = Path(audio_root_dir + target_record_file_path)
                    targetDirectory.mkdir(parents=True, exist_ok=True)
                    rename_and_copy_to(
                        filepath,
                        targetDirectory,
                        audio_file_parameters.filename,
                    )
            
            
            
            
            # Create annotation

            # Set start_time=0.0 & end_time=duration if not given ???
            if not val['start_time']: val['start_time'] = 0.0
            if not val['end_time']: val['end_time'] = audio_file_parameters.duration

            # To check if already in DB --> convert float to decimal with 6 digits (see db format)
            val['start_time'] = '%.6f' % val['start_time']
            val['end_time'] = '%.6f' % val['end_time']
            if val['start_frequency'] is not None:
                val['start_frequency'] = '%.6f' % val['start_frequency']
            if val['end_frequency'] is not None:
                val['end_frequency'] = '%.6f' % val['end_frequency']


            annotation = [
                ('record_id', record_id),

                ('start_time', val['start_time']),
                ('end_time', val['end_time']),
                ('start_frequency', val['start_frequency']),
                ('end_frequency', val['end_frequency']),
                ('channel_ix', val['channel_ix']),
                
                ('individual_id', val['individual_id']),
                ('group_id', val['group_id']),
                
                ('vocalization_type', val['vocalization_type']),
                ('quality_tag', val['quality_tag']),

                ('id_level', val['id_level']),

                ('background_level', val['background_level']),
                ('remarks', val['remarks']),
                
                ('annotator_id', annotator_id),
            ]
            
            #print(annotation)


            

            if species_id and noise_id:
                print('Error, only species or noise accepted but not both!')
            else:

                # Insert annotation data
                annotation_table = None

                if species_id:
                    annotation_table = 'annotation_of_species'
                    annotation.append(('species_id', species_id))
                    annotation.append(('xeno_canto_background', 0))
                
                if noise_id:
                    annotation_table = 'annotation_of_noise'
                    annotation.append(('noise_id', noise_id))  

                if annotation_table:
                    (annotation_id, annotation_created) = get_entry_id_or_create_it(
                        db_cursor,
                        annotation_table,
                        annotation,
                        annotation,
                        info=True,
                    )
                    #print('annotation_id', annotation_id)
                else:
                    print('Warning no annotation tabel match')


            if dry_run is False:
                db_connection.commit()

            print(ix, row['filename'], 'record_id', record_id, record_created, 'annotation_id', annotation_id, annotation_created)
            #print(ix, row['filename'], record_entry)



parser = argparse.ArgumentParser(description='')

parser.add_argument(
    '--path',
    metavar='path',
    type=Path,
    nargs='?',
    help='excel file with all entries',
    default=EXCEL_PATH,
)

args = parser.parse_args()

if __name__ == '__main__':
    import_from_excel(args.path)
