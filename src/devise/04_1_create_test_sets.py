# conda install -c anaconda openpyxl

import os
import numpy as np
import pandas as pd
import soundfile as sf

from mysql.connector import connect, MySQLConnection

root_dir = '/mnt/z/Projekte/DeViSe/'
metadata_dir = root_dir + 'Annotationen/'


db_connection = connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='Password123!?',
    database='libro_animalis',
    auth_plugin='mysql_native_password',
)

def get_start_and_end_times_of_overlapping_segments(global_end_time, global_start_time=0.0, segment_duration=5.0, step_duration=1.0, fit_last_segment_to_global_end_time=True):

    start_times = []
    end_times = []

    start_time = global_start_time
    end_time = start_time + segment_duration

    while end_time < global_end_time:

        start_times.append(start_time)
        end_times.append(end_time)
        
        start_time += step_duration
        end_time = start_time + segment_duration

    if fit_last_segment_to_global_end_time:
        end_time = global_end_time
        start_time = end_time - segment_duration
        if start_time < global_start_time:
            start_time = global_start_time
        start_times.append(start_time)
        end_times.append(end_time)

    return start_times, end_times


def get_annotations_crex_crex():

    keys = ['original_filename', 'start_time', 'end_time']
    #keys += ['start_frequency', 'end_frequency']
    #keys += ['channel_ix']
    #keys += ['vocalization_type']
    keys += ['quality_tag', 'background_level']
    #keys += ['id_level']
    keys += ['file_path', 'filename', 'duration', 'channels']


    print(keys)

    df_dict = {}
    for key in keys:
        df_dict[key] = []

    with db_connection.cursor(dictionary=True) as db_cursor:
        
        query = "SELECT * FROM libro_animalis.annotation_view WHERE collection LIKE '%devise%'"
        query += " AND latin_name = 'Crex crex'"
        query += " AND annotator LIKE 'Beck, Lars'"
        query += " AND original_filename LIKE '%Devise%';"
        
        db_cursor.execute(query)
        rows = db_cursor.fetchall()

        for row in rows:
            for key in keys:
                df_dict[key].append(row[key])
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

        print('n_rows', db_cursor.rowcount)

    df = pd.DataFrame.from_dict(df_dict)
    print(df)

    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v01'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df

def get_annotations_Scolopax_rusticola_of_original_files():

    # Use original files (not annotation db segments)
    # Start from hakan excel file
    # Ignore vocalization_type for now

    # Read hakan excel file
    path = root_dir + 'Annotationen/ARSU_temp/Scolopax_rusticola_Devise_ARSU_2022_v1.xlsx'
    df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")
    #print(df)

    # Edit df to be compatible with crex crex df

    # Remove some cols
    df = df.drop(columns=['channel_ix', 'start_frequency', 'end_frequency', 'vocalization_type', 'id_level', 'comment', 'species_latin_name', 'annotator_name', 'recordist_name', 'location_name', 'record_date', 'record_time', 'collection_name', 'record_filepath'])

    # Rename some cols
    df = df.rename(columns={'filename': 'original_filename', 'quality': 'quality_tag', 'has_background': 'background_level'})

    # Add some cols
    df['file_path'] = None
    df['filename'] = None
    df['duration'] = None
    df['channels'] = None

    # Get duration of files
    filenames = list(df['original_filename'].unique())
    n_files = len(filenames)
    print('n_files', n_files)

    src_dir = '/mnt/z/Projekte/DeViSe/Annotationen/ARSU_temp/Scolopax_rusticola_Devise_ARSU_2022/'

    file_counter = 0
    for filename in filenames:
        path = src_dir + filename + '.flac'
        with sf.SoundFile(path) as f:
            duration = f.frames/f.samplerate
        # Set duration in df
        df.loc[df['original_filename'] == filename, 'duration'] = duration
        #print(file_counter, filename, duration)
        file_counter += 1


    print(df)

    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v01'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df


def get_annotations_Scolopax_rusticola():

    keys = ['original_filename', 'start_time', 'end_time']
    #keys += ['start_frequency', 'end_frequency']
    #keys += ['channel_ix']
    #keys += ['vocalization_type']
    keys += ['quality_tag', 'background_level']
    #keys += ['id_level']
    keys += ['file_path', 'filename', 'duration', 'channels']


    print(keys)

    df_dict = {}
    for key in keys:
        df_dict[key] = []

    with db_connection.cursor(dictionary=True) as db_cursor:
        
        query = "SELECT * FROM libro_animalis.annotation_view WHERE collection LIKE '%devise%'"
        query += " AND latin_name = 'Scolopax rusticola'"
        query += " AND annotator LIKE 'Steinkamp%'"
        query += " AND date>='2022-01-01';"
        
        db_cursor.execute(query)
        rows = db_cursor.fetchall()

        for row in rows:
            for key in keys:
                df_dict[key].append(row[key])
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

        print('n_rows', db_cursor.rowcount)

    df = pd.DataFrame.from_dict(df_dict)
    print(df)

    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v01'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df

def get_annotations_Scolopax_rusticola_absent():

    keys = ['original_filename', 'start_time', 'end_time']
    #keys += ['start_frequency', 'end_frequency']
    #keys += ['channel_ix']
    #keys += ['vocalization_type']
    keys += ['quality_tag', 'background_level']
    #keys += ['id_level']
    keys += ['file_path', 'filename', 'duration', 'channels']


    print(keys)

    df_dict = {}
    for key in keys:
        df_dict[key] = []

    with db_connection.cursor(dictionary=True) as db_cursor:
        
        query = "SELECT * FROM libro_animalis.annotation_of_noise_view WHERE collection LIKE '%devise%'"
        query += " AND noise_name = 'Scolopax rusticola absent'"
        query += " AND annotator LIKE 'Steinkamp%'"
        query += " AND date>='2022-01-01';"
        
        db_cursor.execute(query)
        rows = db_cursor.fetchall()

        for row in rows:
            for key in keys:
                df_dict[key].append(row[key])
            print(row['id'], row['start_time'], row['end_time'], row['start_frequency'], row['end_frequency'], row['vocalization_type'])

        print('n_rows', db_cursor.rowcount)

    df = pd.DataFrame.from_dict(df_dict)
    print(df)

    # Hack: set start/end time to 0.0 because otherwise interval will be interpreted as species annotation
    df['start_time'] = 0.0
    df['end_time'] = 0.0

    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v01'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df


def create_test_segments(df, segment_duration=5.0, species_latin_name='Crex crex'):

    # Sort by file and start time
    df_src = df.sort_values(['original_filename', 'start_time']).reset_index(drop=True)

    # Sanity checks and corrections for start_time (shoud not be negative)
    if not df_src.loc[df_src['start_time'] < 0.0].empty:
        print('Warning negative start_time:', df_src.loc[df_src['start_time'] < 0.0])
    df_src.loc[df_src['start_time'] < 0.0, 'start_time'] = 0.0

    # Init new df dict (same cols as df_src)
    keys = list(df_src.columns)
    # Add species/noise col
    keys += ['species_latin_name']
    df_dict = {}
    for key in keys:
        df_dict[key] = []

    # Iterate over files
    filenames = list(df_src['original_filename'].unique())
    n_files = len(filenames)
    print('n_files', n_files)

    file_counter = 0
    for filename in filenames:

        #if file_counter > 1: break

        df_filename = df_src[df_src['original_filename']==filename].reset_index(drop=True)
        
        # Sanity check duration all equal for same file
        assert(df_filename['duration'] == df_filename['duration'][0]).all()


        # Sanity check and correction for end_time > duration
        if not df_filename.loc[df_filename['end_time'] > df_filename['duration']].empty:
            print('Warning end_time > duration:', df_filename.loc[df_filename['end_time'] > df_filename['duration']])
            df_filename.loc[df_filename['end_time'] > df_filename['duration'], 'end_time'] = df_filename['duration']


        #print(df_filename)

        # Get new time intervals (start and end times) without overlap
        global_end_time = df_filename['duration'][0]
        start_times, end_times = get_start_and_end_times_of_overlapping_segments(global_end_time, global_start_time=0.0, segment_duration=segment_duration, step_duration=segment_duration, fit_last_segment_to_global_end_time=True)

        n_segments = len(start_times)
        for ix in range(n_segments):

            # Copy file infos (use first entry)
            df_dict['original_filename'].append(df_filename['original_filename'][0])
            df_dict['file_path'].append(df_filename['file_path'][0])
            df_dict['filename'].append(df_filename['filename'][0])
            df_dict['duration'].append(df_filename['duration'][0])
            df_dict['channels'].append(df_filename['channels'][0])
            
            start_time = start_times[ix]
            end_time = end_times[ix]

            # Use new start/end times
            df_dict['start_time'].append(start_time)
            df_dict['end_time'].append(end_time)

            # Get minimum of quality_tag and background_level 
            # from all src intervals
            # starting or ending in new interval (with min overlap/intersection?)
            min_overlap = 0.0 #0.1   # 100 ms
            df_filtered = df_filename.loc[
                (df_filename['start_time'] + min_overlap < end_time) &
                (df_filename['end_time'] - min_overlap > start_time)
                ]

            print(file_counter, filename, ix, start_time)

            if df_filtered.empty:
                df_dict['species_latin_name'].append(None)
                df_dict['quality_tag'].append(None)
                df_dict['background_level'].append(None)
            else:
                df_dict['species_latin_name'].append(species_latin_name)
                # Use min value of org segments
                df_dict['quality_tag'].append(df_filtered['quality_tag'].min())
                df_dict['background_level'].append(df_filtered['background_level'].min())

                #print(df_filtered)


        file_counter += 1

    df = pd.DataFrame.from_dict(df_dict)
    print(df)

    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v02'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df


def split_test_set_via_quality(df):

    # Convert cols quality_tag and background_level to numeric
    df['quality_tag'] = pd.to_numeric(df['quality_tag'])
    df['background_level'] = pd.to_numeric(df['background_level'])

    print(df)

    filenames_all = list(df['original_filename'].unique())
    n_files_all = len(filenames_all)
    print('n_files_all', n_files_all)

    n_segments_all = len(df.index)
    print('n_segments_all', n_segments_all)


    df_quality_below_3 = df.loc[(df['quality_tag'] < 3)]
    n_segments_quality_below_3 = len(df_quality_below_3.index)
    print('n_segments_quality_below_3', n_segments_quality_below_3) # 1136

    df_quality_below_4 = df.loc[(df['quality_tag'] < 4)]
    n_segments_quality_below_4 = len(df_quality_below_4.index)
    print('n_segments_quality_below_4', n_segments_quality_below_4) # 5854

    df_quality_above_3 = df.loc[(df['quality_tag'] > 3)]
    n_segments_quality_above_3 = len(df_quality_above_3.index)
    print('n_segments_quality_above_3', n_segments_quality_above_3) # 4613

    # Get files with good quality (< 4) segments
    filenames_easy = list(df_quality_below_4['original_filename'].unique())
    n_files_easy = len(filenames_easy)
    print('n_files_easy', n_files_easy) # 132

    filenames_hard = list(df_quality_above_3['original_filename'].unique())
    n_files_hard = len(filenames_hard)
    print('n_files_hard_n_easy', n_files_hard) # 127 (but files can also have segments with good quality!)

    # # Add test split type (init with test_hard)
    # # test_hard has only quality > 3 segments
    # df['split'] = 'test_hard'
    # df.loc[df['original_filename'].isin(filenames_easy), 'split'] = 'test_easy'

    # Add test split type (init with test_easy)
    # test_easy has only quality < 4 segments
    df['split'] = 'test_easy'
    df.loc[df['original_filename'].isin(filenames_hard), 'split'] = 'test_hard'

    print(df)


    # Get some final stats

    df_easy = df.loc[(df['split'] == 'test_easy')]
    
    filenames_easy = list(df_easy['original_filename'].unique())
    n_files_easy = len(filenames_easy)
    print('n_files_easy', n_files_easy)
    n_segments_easy = len(df_easy.index)
    print('n_segments_easy', n_segments_easy)
    n_segments_positiv_easy = len(df_easy.loc[df_easy['species_latin_name'] != ''])
    print('n_segments_positiv_easy', n_segments_positiv_easy)
    n_segments_negativ_easy = len(df_easy.loc[df_easy['species_latin_name'] == ''])
    print('n_segments_negativ_easy', n_segments_negativ_easy)
    assert n_segments_positiv_easy + n_segments_negativ_easy == n_segments_easy


    df_hard = df.loc[(df['split'] == 'test_hard')]

    filenames_hard = list(df_hard['original_filename'].unique())
    n_files_hard = len(filenames_hard)
    print('n_files_hard', n_files_hard)
    n_segments_hard = len(df_hard.index)
    print('n_segments_hard', n_segments_hard)
    n_segments_positiv_hard = len(df_hard.loc[df_hard['species_latin_name'] != ''])
    print('n_segments_positiv_hard', n_segments_positiv_hard)
    n_segments_negativ_hard = len(df_hard.loc[df_hard['species_latin_name'] == ''])
    print('n_segments_negativ_hard', n_segments_negativ_hard)
    assert n_segments_positiv_hard + n_segments_negativ_hard == n_segments_hard

    assert n_segments_easy + n_segments_hard == n_segments_all


    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v04'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df

def split_test_set_via_quality_relative_to_files_before_segmentation(df):

    # Convert cols quality_tag and background_level to numeric
    df['quality_tag'] = pd.to_numeric(df['quality_tag'])
    df['background_level'] = pd.to_numeric(df['background_level'])

    # Add col of original filename before segmentation
    # e.g. Devise01_2022-06-13T21-12-18_s00000000ms_c0.wav --> Devise01_2022-06-13T21-12-18
    df['original_filename_before_segmentation'] = None
    for ix, row in df.iterrows():
        df.at[ix, 'original_filename_before_segmentation'] = row['original_filename'][:-19]

    print(df)

    filenames_all = list(df['original_filename_before_segmentation'].unique())
    n_files_all = len(filenames_all)
    print('n_files_all', n_files_all)

    n_segments_all = len(df.index)
    print('n_segments_all', n_segments_all)


    df_quality_below_3 = df.loc[(df['quality_tag'] < 3)]
    n_segments_quality_below_3 = len(df_quality_below_3.index)
    print('n_segments_quality_below_3', n_segments_quality_below_3) # 1136

    df_quality_below_4 = df.loc[(df['quality_tag'] < 4)]
    n_segments_quality_below_4 = len(df_quality_below_4.index)
    print('n_segments_quality_below_4', n_segments_quality_below_4) # 5854

    df_quality_above_3 = df.loc[(df['quality_tag'] > 3)]
    n_segments_quality_above_3 = len(df_quality_above_3.index)
    print('n_segments_quality_above_3', n_segments_quality_above_3) # 4613

    # Get files with good quality (< 4) segments
    filenames_easy = list(df_quality_below_4['original_filename_before_segmentation'].unique())
    n_files_easy = len(filenames_easy)
    print('n_files_easy', n_files_easy) # 132

    filenames_hard = list(df_quality_above_3['original_filename_before_segmentation'].unique())
    n_files_hard = len(filenames_hard)
    print('n_files_hard_n_easy', n_files_hard) # 127 (but files can also have segments with good quality!)

    # # Add test split type (init with test_hard)
    # # test_hard has only quality > 3 segments
    #df['split'] = 'test_hard'
    #df.loc[df['original_filename_before_segmentation'].isin(filenames_easy), 'split'] = 'test_easy'

    # Add test split type (init with test_easy)
    # test_easy has only quality < 4 segments
    df['split'] = 'test_easy'
    df.loc[df['original_filename_before_segmentation'].isin(filenames_hard), 'split'] = 'test_hard'

    print(df)


    # Get some final stats

    df_easy = df.loc[(df['split'] == 'test_easy')]
    
    filenames_easy = list(df_easy['original_filename_before_segmentation'].unique())
    n_files_easy = len(filenames_easy)
    print('n_files_easy', n_files_easy)
    n_segments_easy = len(df_easy.index)
    print('n_segments_easy', n_segments_easy)
    n_segments_positiv_easy = len(df_easy.loc[df_easy['species_latin_name'] != ''])
    print('n_segments_positiv_easy', n_segments_positiv_easy)
    n_segments_negativ_easy = len(df_easy.loc[df_easy['species_latin_name'] == ''])
    print('n_segments_negativ_easy', n_segments_negativ_easy)
    assert n_segments_positiv_easy + n_segments_negativ_easy == n_segments_easy


    df_hard = df.loc[(df['split'] == 'test_hard')]

    filenames_hard = list(df_hard['original_filename_before_segmentation'].unique())
    n_files_hard = len(filenames_hard)
    print('n_files_hard', n_files_hard)
    n_segments_hard = len(df_hard.index)
    print('n_segments_hard', n_segments_hard)
    n_segments_positiv_hard = len(df_hard.loc[df_hard['species_latin_name'] != ''])
    print('n_segments_positiv_hard', n_segments_positiv_hard)
    n_segments_negativ_hard = len(df_hard.loc[df_hard['species_latin_name'] == ''])
    print('n_segments_negativ_hard', n_segments_negativ_hard)
    assert n_segments_positiv_hard + n_segments_negativ_hard == n_segments_hard

    assert n_segments_easy + n_segments_hard == n_segments_all

    # Drop col
    df = df.drop(columns=['original_filename_before_segmentation'])


    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v04'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

    return df





    





##################################################################################################

#df = get_annotations_crex_crex()

#metadata_path_without_ext = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v01'
#df = pd.read_excel(metadata_path_without_ext + '.xlsx', keep_default_na=False, engine="openpyxl")
#df = create_test_segments(df)

#metadata_path_without_ext = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v02_5s'
#df = pd.read_excel(metadata_path_without_ext + '.xlsx', keep_default_na=False, engine="openpyxl")
#df = split_test_set_via_quality(df)



# Use orignal files and annotations
#df = get_annotations_Scolopax_rusticola_of_original_files()

# Use segments in DB 
# df = get_annotations_Scolopax_rusticola()
# df_noise = get_annotations_Scolopax_rusticola_absent()
# df = pd.concat([df, df_noise], ignore_index=True, sort=False).reset_index(drop=True)
# metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v01'
# df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')


# metadata_path_without_ext = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaAnnotations_v21'
# df = pd.read_excel(metadata_path_without_ext + '.xlsx', keep_default_na=False, engine="openpyxl")
# df = create_test_segments(df, species_latin_name='Scolopax rusticola')

#metadata_path_without_ext = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaAnnotations_v22_5s'
#df = pd.read_excel(metadata_path_without_ext + '.xlsx', keep_default_na=False, engine="openpyxl")
#df = split_test_set_via_quality(df)
#df = split_test_set_via_quality_relative_to_files_before_segmentation(df)


print('Done.')