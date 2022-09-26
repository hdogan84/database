# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import numpy as np
import pandas as pd
import soundfile as sf

root_dir = '/mnt/z/Projekte/DeViSe/'
metadata_dir = root_dir + 'Annotationen/'

#lars_dir = '/mnt/z/AG/TSA/Lars_Beck/'
lars_dir = metadata_dir + 'Lars_Beck/'


def create_postfix_str(start_time, end_time=None):
    # _500To20000ms
    #postfix_str = '_' + str(int(1000*start_time)) + 'To' + str(int(1000*end_time)) + 'ms'
    # S00000500E00002000ms
    #postfix_str = '_S' + str(int(1000*start_time)).zfill(8) + 'E' + str(int(1000*end_time)).zfill(8) + 'ms'
    # S00000500ms
    postfix_str = '_s' + str(int(1000*start_time)).zfill(8) + 'ms'

    # Olaf style Shhmmss.ssEhhmmss.ss

    return postfix_str


def read_audacity_label_file(path, ignore_freq_range=False):

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    # Read audacity label track txt file
    df = pd.read_csv(path, sep='\t', header=None)
    #print(df)

    # Add header
    #df.columns = ['start_time', 'end_time', 'label']

    # Check if frequency ranges are included (every 2nd row starts with \)
    # Example, e.g.:
    '''
    1192.760530	1193.424606	sp=Scolopax rusticola; ct=gr; ql=4; bg=2
    \	-1.000000	510.638306
    1193.424606	1193.522416	sp=Scolopax rusticola; ct=sq; ql=4; bg=2
    \	5361.702148	5531.914551
    '''

    # Check for NaN values
    if df.isnull().values.any():
        print('Error: NaN value', path)
        return None
    else:

        # Check if "\" is at 2nd row first col  
        if len(df.index) > 1 and df.iat[1,0] == '\\':
            has_freq_range = True
            print('freq range info included in label file')
        else:
            has_freq_range = False

        if has_freq_range:
            
            if ignore_freq_range:
                # Remove freq range rows starting with \ (all odd rows) if ignore_freq_range
                df = df.drop(df[df.iloc[:, 0] == '\\'].index).reset_index(drop=True)
                # Add header
                df.columns = ['start_time', 'end_time', 'label']
            else:
                # Include freq range as new cols start_freq and end_freq

                # Get start & end freq
                df_freq = df[df.iloc[:, 0] == '\\']
                start_freq_list = df_freq.iloc[:, 1].tolist()
                end_freq_list = df_freq.iloc[:, 2].tolist()
                #print(df_freq)

                # Remove freq range rows starting with \ (all odd rows)
                df = df.drop(df[df.iloc[:, 0] == '\\'].index).reset_index(drop=True)
                # Add header
                df.columns = ['start_time', 'end_time', 'label']

                # Add cols
                df['start_freq'] = start_freq_list
                df['end_freq'] = end_freq_list

                # Reorder cols
                df = df[['start_time', 'end_time', 'start_freq', 'end_freq', 'label']]
                #print(df)

        else:
            # Add header
            df.columns = ['start_time', 'end_time', 'label']

        #print(df)
        return df

def process_audacity_label_data(df, check_label_data=True):

    '''
    example of label: sp=Crex crex; ct=s; ql=2; id=1; bg=0; cm=Hallo

    Artname (sp): Crex crex
    Lauttyp (ct): vorerst 3: s=Gesang, c=Ruf, i=instrumental (Trommeln o.ä.)
    Qualität (ql): 1 bis 5; 1 – sehr gut; 2 – gut; 3 – brauchbar; 4 – sehr schlecht; 5 – gerade noch zu hören
    Sicherheit d. Identifikation (id): 1 – zu 100% sicher, 2 – sehr sicher, 3 – unsicher
    Hintergrund (bg): 0 – kein Hintergrund; 1 – im Hintergrund andere Art, aber deutlich leiser; 2 - im Hintergrund andere Art deutlich
    Freies Feld (cm): alle anderen Kommentare
    '''

    assignment_operator = '='
    separator = ';'

    key_tags = ['sp', 'ct', 'ql', 'id', 'bg', 'cm']
    key_names = ['species', 'call_type', 'quality', 'id_level', 'background_level', 'comment']

    # ToDo: Sanity checks
    # assignment_operator, separator correct
    # what key_tags are used
    # are number of key_tags always the same

    n_rows = len(df.index)

    label_df_dict = {}
    for key in key_tags:
        label_df_dict[key] = [None] * n_rows

    for ix, row in df.iterrows():
        label_str = row['label']
        # Remove leading and trailing whitespaces
        label_str = label_str.strip()
        # Remove leading and trailing separators
        label_str = label_str.strip(separator)

        #print(ix, label_str)

        # Split into labels
        labels = label_str.split(separator)
        #print(labels)

        
        for label in labels:
            # Remove leading and trailing whitespaces
            label = label.strip()
            #print(label)
            key_value_pair = label.split(assignment_operator)
            #print(key_value_pair)
            key = key_value_pair[0]
            value = key_value_pair[1]
            #print(key, value)
            
            if key not in key_tags:
                print('Error: Undefined key', key, ix, label)
            else:
                # Dequote comment string: "comment" --> comment
                if key == 'cm' and value[0] == value[-1] and value.startswith(("'", '"')):
                    value = value[1:-1]

                label_df_dict[key][ix] = value

    #print(label_df_dict)

    # Check if there are label without any/some data
    if check_label_data:
        for key in key_tags:
            if label_df_dict[key].count(None) == len(label_df_dict[key]):
                print(key, 'has no data at all')
            else:
                if label_df_dict[key].count(None) > 0:
                    print(key, 'has no data sometimes')

    label_df = pd.DataFrame.from_dict(label_df_dict)
    # Rename cols (e.g. sp --> species)
    label_df.columns = key_names
    #print(label_df)

    # Remove label col from original df
    df = df.drop(columns=['label'])

    # Merge original df with extracted label df
    assert len(df.index) == len(label_df.index)
    df_concatenated = pd.concat([df, label_df], axis="columns")
    #print(df_concatenated)

    return df_concatenated


#path = lars_dir + 'Unteres_Odertal_2021_06_10/Devise02_2021-06-10T22-38-32_Pos01.txt'
#path = metadata_dir + '_BackupML/Devise07_2022-05-09T20-40-27_Annotation.txt'
path = lars_dir + 'Criewen_2022_05_15/Criewen02/CRIEWEN02_20220515_202400.txt'
# df = read_audacity_label_file(path)
# df = process_audacity_label_data(df)
# print(df)

def read_raven_label_file(path):

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    # Read audacity label track txt file
    df = pd.read_csv(path, sep='\t')
    #print(df)
    return df

path = root_dir + 'Scolopax_rusticola_Recordings/Monitoring/Peenemuende_140525_327_4ch.Table.1.selections.txt'
#read_raven_label_file(path)

def write_part_of_audio_file(path, start_time, end_time, channel_ix=None, dst_dir=None, format=None):

    # ToDo Maybe: resample, remove dc-offset (hp filter), normalize, fade in/out

    # Get filename and extension
    filename = os.path.basename(path)
    [filename_without_ext, ext] = os.path.splitext(filename)
    
    # Get destination directory
    if not dst_dir:
        # Use same dir as src file path
        dst_dir = os.path.dirname(path) + '/'
    if dst_dir[-1] != '/':
        dst_dir += '/'
    if not os.path.exists(dst_dir): 
        os.makedirs(dst_dir)

    if os.path.isfile(path):
        
        # Get audio file infos
        with sf.SoundFile(path) as f:
            samplerate = f.samplerate
            n_channels = f.channels
            subtype = f.subtype # bit depth info, e.g. 'PCM_16', 'PCM_24'

        start_ix = int(start_time*samplerate)
        end_ix = int(end_time*samplerate)
        data, samplerate = sf.read(path, start=start_ix, stop=end_ix, always_2d=True)

        filename_new = filename_without_ext + create_postfix_str(start_time)
        if channel_ix is not None:
            filename_new += '_c' + str(channel_ix)

        if format:
            ext = '.' + format
        
        path_new = dst_dir + filename_new + ext

        if channel_ix is not None:
            sf.write(path_new, data[:,channel_ix], samplerate, subtype=subtype)
        else:
            sf.write(path_new, data, samplerate, subtype=subtype)
        
    else:
        print('Error file not found', path)


def get_open_intervals(df, global_start_time=0.0, global_end_time=None):
    
    # Input: df with intervals (start_time, end_time)
    # Output: df with open intervals not intersecting with input intervals
    
    df_new_dict = {}
    df_new_dict['start_time'] = []
    df_new_dict['end_time'] = []

    # Get list of dicts (pairs of time, start/stop event type)
    events = []
    for ix, row in df.iterrows():
        event = {'time': row['start_time'], 'type': 'start_time'}
        events.append(event)
        event = {'time': row['end_time'], 'type': 'end_time'}
        events.append(event)

    # Sort by time
    events = sorted(events, key=lambda d: d['time']) 
    #print(events)

    start_time = 0.0
    counter = 0
    for event in events:

        if counter == 0 and event['time'] > global_start_time:
            df_new_dict['start_time'].append(start_time)
            df_new_dict['end_time'].append(event['time'])

        if event['type'] == 'start_time': counter +=1
        else: counter -=1

        start_time = event['time']
    
    # Get last interval if last end_time < global_end_time
    if global_end_time and global_end_time > start_time:
        df_new_dict['start_time'].append(start_time)
        df_new_dict['end_time'].append(global_end_time)

    # Convert to df
    df_new = pd.DataFrame.from_dict(df_new_dict)
    #print(df_new) 

    return df_new

def create_noise_annotations(df, dilation_duration=1.0, min_duration=5.0):
    
    # Create dataframe with anti/none annotations (all intervals without annotation for each filename)

    # Cols belonging to annoations that get meaningless
    cols_set_to_none = ['start_frequency', 'end_frequency', 'individual_id', 'group_id', 'vocalization_type', 'quality_tag', 'id_level', 'background_level', 'remarks', 'xeno_canto_background', 'species_latin_name']

    # Create df_dilation (add time interval to start/end time)
    df_dilation = df.copy()
    df_dilation['start_time'] = df_dilation['start_time'] - dilation_duration
    df_dilation['end_time'] = df_dilation['end_time'] + dilation_duration

    # Check/correkt if start_time < 0.0 (ToDo: end_time > duration)
    df_dilation.loc[df_dilation['start_time'] < 0.0, 'start_time'] = 0.0

    # Sort by filename and start_time
    df_dilation = df_dilation.sort_values(['filename', 'start_time']).reset_index(drop=True)
    #print(df_dilation[10:20])

    # Create new df with same cols
    cols = df_dilation.columns
    #print(list(cols))
    df_new = pd.DataFrame(columns=cols)

    filenames = list(df['filename'].unique())
    n_files = len(filenames)

    counter = 0
    for filename in filenames:

        #if counter > 4: break

        df_filename = df_dilation[df_dilation['filename']==filename].reset_index(drop=True)
        #print(df_filename)

        # Get duration
        path = df_filename.record_filepath.values[0]
        with sf.SoundFile(path) as f:
            duration = f.frames/f.samplerate


        df_filename_noise = get_open_intervals(df_filename, global_start_time=0.0, global_end_time=duration)

        # Filter intervals >= min_duration
        df_filename_noise = df_filename_noise[(df_filename_noise['end_time'] - df_filename_noise['start_time'] >= min_duration)].reset_index(drop=True)
        #print(df_filename_noise)

        # Add org recording metadata
        for ix, row in df_filename_noise.iterrows():
            # Append first row of df_filename
            df_new = df_new.append(df_filename.iloc[0]).reset_index(drop=True)
            # Change start/end_time
            df_new.at[df_new.index[-1], 'start_time'] = row['start_time']
            df_new.at[df_new.index[-1], 'end_time'] = row['end_time']

        counter += 1

    # Set cols with annoation individual values to None
    for col in cols_set_to_none:
        if col in cols:
            df_new[col] = None

    #print(df_new)

    return df_new


def process_Crex_crex_Unteres_Odertal_2017():


    write_audio_files = False # True False
    write_metadata = True

    audio_root_src_dir = root_dir + 'Crex_crex_annotated/Crex_crex_Unteres_Odertal_2017_annotated/'
    audio_root_dst_dir = root_dir + 'Annotationen/_Segments/'

    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/Crex_crex_Unteres_Odertal_2017_v02'

    collection_name = 'devise'
    
    # Read excel file
    path = metadata_dir + 'Crex_crex_Unteres_Odertal_2017.xlsx'

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    df = pd.read_excel(path, engine='openpyxl')
    #print(df)
    print('n_rows', len(df))

    filenames = df['filename'].unique()
    n_filenames = len(filenames)
    #print(filenames)
    print('n_filenames', n_filenames)

    # df_new stuff
    df_new_dict = {}
    keys = ['filename', 'species_latin_name', 'noise_name', 'record_date', 'record_filepath']
    for key in keys:
        df_new_dict[key] = []


    for ix, row in df.iterrows():

        #if ix > 10: break
        #print(ix, row['filename'])

        filename = row['filename']
        start_time = row['start_time']
        end_time = row['end_time']
        channel_ix = row['channel_ix']

        if row['class'] == 'Crex crex':
            dst_sub_dir = 'Crex_crex'
            df_new_dict['species_latin_name'].append(row['class'])
            df_new_dict['noise_name'].append(None)
        if row['class'] == 'BG':
            dst_sub_dir = 'Crex_crex_BG'
            df_new_dict['species_latin_name'].append(None)
            df_new_dict['noise_name'].append('Crex crex absent')

        path = audio_root_src_dir + row['sub_dir'] + '/' + filename + '.wav'

        if not os.path.isfile(path):
            print("Error: File not found", path)
            continue
        
            
        dst_dir = audio_root_dst_dir + dst_sub_dir + '/'

        if write_audio_files:    
            write_part_of_audio_file(path, start_time, end_time, channel_ix=channel_ix, dst_dir=dst_dir)


        filename_new = filename + create_postfix_str(start_time) + '_c' + str(channel_ix)

        df_new_dict['filename'].append(filename_new)
        
        date_str = filename.split('_')[3]
        date = date_str[:4] + '-' + date_str[4:6] + '-' + date_str[6:8]
        df_new_dict['record_date'].append(date)

        filenamepath_new = dst_dir + filename_new + '.wav'
        df_new_dict['record_filepath'].append(filenamepath_new)


        print(filename, filename_new)


    df_new = pd.DataFrame.from_dict(df_new_dict)

    # Add infos
    df_new['id_level'] = 1
    df_new['vocalization_type'] = 'song'
    
    df_new['recordist_name'] = 'Frommolt, Karl-Heinz'
    df_new['annotator_name'] = 'Frommolt, Karl-Heinz'
    df_new['location_name'] = 'Unteres Odertal'
    df_new['collection_name'] = collection_name

    print(df_new)

    # Write metadata (excel, csv)
    if write_metadata:
        df_new.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')
        df_new.to_csv(metadata_path_without_ext + '.csv', index=False)

#process_Crex_crex_Unteres_Odertal_2017()

def process_fva():

    write_metadata = False # True False
    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_FVA_v01'


    audio_src_dir = metadata_dir + 'Scolopax_rusticola_FVA_BadenWürttemberg/Dateien_MFN_FVA/'

    # Read excel file
    path = metadata_dir + 'Scolopax_rusticola_FVA_BadenWürttemberg/220722_fva_selections.csv'

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    #encoding = 'cp1252'
    encoding = 'ISO-8859-1'
    df = pd.read_csv(path, sep=';', encoding=encoding)
    #print(df.columns.values.tolist())
    
    # Drop cols not used (yet)
    df = df.drop(columns=[' "id"', 'Unnamed: 0', 'deploy_id', 'dateiname', 'selection', 'view', 'channel', 'species_code', 'common_name', 'import'])

    # Sort by (new) file name and begin_time
    df = df.sort_values(['new_name', 'begin_time']).reset_index(drop=True)

    #print(df[10:30])

    print("n_annotations", len(df)) # 2497

    # Get unique audio files
    files = list(df['new_name'].unique())
    n_files = len(files)
    #print(files)
    print('n_files', n_files) # 369 (10min, mono, 48 kHz)

    # Get unique anmerkung
    remarks = list(df['anmerkung'].unique())
    n_remarks = len(remarks)
    #print(remarks)
    print('n_remarks', n_remarks) # 64

    # Rename cols
    df = df.rename(columns={'new_name': 'filename', 'begin_time': 'start_time', 'low_freq': 'start_frequency', 'high_freq': 'end_frequency', 'anmerkung': 'remarks'})
    
    # Add metadata
    
    df['record_date'] = None
    df['record_time'] = None

    df['vocalization_type'] = None
    df['quality_tag'] = 3
    df['record_filepath'] = None

    
    for ix, row in df.iterrows():

        # Get vocalization_type from anmerkung (remarks)
        remark = row['remarks']
        if 'puitzen' in remark and not 'quorren' in remark:
            df.at[ix, 'vocalization_type'] = 'squeak'
        if not 'puitzen' in remark and 'quorren' in remark:
            df.at[ix, 'vocalization_type'] = 'grunt'

        # # ToDo: correct/add type depending on start/end_frequency
        # if row['start_frequency'] > 1800.0 and row['end_frequency'] > 9000.0:
        #     df.at[ix, 'vocalization_type'] = 'squeak'
        # if row['end_frequency'] < 5000.0:
        #     t=1



        # Get quality from anmerkung
        if 'gut' in remark:
            df.at[ix, 'quality_tag'] = 2
        if 'sehr gut' in remark or 'laut' in remark or 'deutlich' in remark:
            df.at[ix, 'quality_tag'] = 1
        if 'leise' in remark or 'Knacken' in remark or 'Regen' in remark or 'schlechte Qualität' in remark:
            df.at[ix, 'quality_tag'] = 4
        if 'sehr leise' in remark:
            df.at[ix, 'quality_tag'] = 5

        # Get date, time from filename
        parts = row['filename'].split('_')
        date_str = parts[6]
        df.at[ix, 'record_date'] = date_str[:4] + '-' + date_str[4:6] + '-' + date_str[6:10]
        time_str = parts[7]
        df.at[ix, 'record_time'] = time_str[:2] + ':' + time_str[2:4] + ':' + time_str[4:6]

        # Get record_filepath
        df.at[ix, 'record_filepath'] = audio_src_dir + row['filename']

        #print(ix, remark, date_str, time_str)
    
    
    #print(df[:8])

    # Add more global metadata
    df['location_name'] = 'Baden-Württemberg'
    df['record_license'] = 'Usage restricted for training devise models!'
    df['record_remarks'] = 'Provided by Forstliche Versuchs- und Forschungsanstalt Baden-Württemberg (FVA). Only use for training (devise) models!'
    df['equipment_name'] = 'AudioMoth'
    df['equipment_sound_device'] = 'AudioMoth'
    df['equipment_microphone'] = 'MEMS'
    df['species_latin_name'] = 'Scolopax rusticola'
    df['collection_name'] = 'FVA (devise)' # ?

    #print(df[:8])

    # Create noise (species absent) annotations
    df_noise_annotations = create_noise_annotations(df)
    df_noise_annotations['noise_name'] = 'Scolopax rusticola absent'
    
    # Concat dfs
    df['noise_name'] = None
    df = pd.concat([df, df_noise_annotations], ignore_index=True, sort=False).reset_index(drop=True)
    
    # Write metadata (excel, csv)
    if write_metadata:
        df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')
        #df.to_csv(metadata_path_without_ext + '.csv', index=False)
    
    print(df)

#process_fva()

def process_hakan_schoenow():

    write_audio_parts = False # True False
    write_metadata = True
    
    src_dir = root_dir + 'Scolopax_rusticola_Recordings/Monitoring/'
    dst_dir = root_dir + 'Annotationen/_Segments/Scolopax_rusticola/'
    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_MfN_Peenemuende+Schoenow_v04'

    # Collect annotations from excel files
    xlsx_files = [
        'Scolopax_rusticola_MfN_Schoenow_2007.xlsx',
        'Scolopax_rusticola_MfN_Schoenow_2008.xlsx',
        'Scolopax_rusticola_MfN_Schoenow_2009.xlsx',
        'Scolopax_rusticola_MfN_Peenemuende_2014.xlsx']

    df_list = []
    for file in xlsx_files:
        path = metadata_dir + file

        if not os.path.isfile(path): 
            print('Error: File not found', path)

        df = pd.read_excel(path, engine='openpyxl')
        print(df)
        #print('n_rows', len(df))
        df_list.append(df)


    # Concat and sort
    df = pd.concat(df_list).reset_index(drop=True)
    df = df.sort_values(['filename', 'start_time']).reset_index(drop=True)

    # Remove sub_dir col
    df = df.drop(columns=['sub_dir'])

    print(df)


    # Get unique audio files
    files = list(df['filename'].unique())
    n_files = len(files)
    print(files) # 'Peenemuende_140525_327_4ch', 'Schoenow_070401051656', 'Schoenow_070408045029', 'Schoenow_070505034545', 'Schoenow_070513034003', 'Schoenow_070520032033', 'Schoenow_070527032221', 'Schoenow_070603030318', 'Schoenow_070617025602', 'Schoenow_070624032240', 'Schoenow_080315061117', 'Schoenow_Ed2_080413045352', 'Schoenow_R4_1_090316050122', 'Schoenow_R4_1_090410040958']
    print('n_files', n_files)

    #quit()


    # Sanity checks (end_time - start_time = 5s)
    for ix, row in df.iterrows():
        if row['end_time'] - row['start_time'] != 5:
            print('Warning end_time-start_time != 5', ix)


    df_hakan = df.copy()

    # Create df with original annotations from Karl
    annotations_org_dir = root_dir + 'Scolopax_rusticola_Recordings/Monitoring/'
    df_annotations_org_list = []
    for file in files:
        path = annotations_org_dir + file + '.Table.1.selections.txt'
        if not os.path.isfile(path): print('Error: File not found', path)
        df = read_raven_label_file(path)

        # Drop cols Selection, View, Species
        df = df.drop(columns=['Selection', 'View', 'Species'])
        # Rename cols
        df = df.rename(columns={'Channel': 'channel_ix', 'Begin Time (s)': 'start_time', 'End Time (s)': 'end_time', 'Low Freq (Hz)': 'start_frequency', 'High Freq (Hz)': 'end_frequency'})
        # Rename Calltype, Soundtype, calltype --> vocalization_type
        df = df.rename(columns={'Calltype': 'vocalization_type'})
        df = df.rename(columns={'Soundtype': 'vocalization_type'})
        df = df.rename(columns={'calltype': 'vocalization_type'})
        # Subtract 1 for channel values
        df['channel_ix'] = df['channel_ix'] - 1
        # Add filename col
        df['filename'] = file
        # Reorder cols
        df = df[['filename', 'channel_ix', 'start_time', 'end_time', 'start_frequency', 'end_frequency', 'vocalization_type']]
        # Rename vocalization_type 1: sq, 2: gr (grunt, squeak)
        df.loc[df['vocalization_type'] == 1, 'vocalization_type'] = 'squeak'
        df.loc[df['vocalization_type'] == 2, 'vocalization_type'] = 'grunt'

        # Drop duplicates (e.g. both views are annotated Waveform 1 & Spectrogram 1)
        df = df.drop_duplicates().reset_index(drop=True)

        
        #print(df)

        df_annotations_org_list.append(df)

    # Concat and sort
    df_annotations_org = pd.concat(df_annotations_org_list).reset_index(drop=True)
    df_annotations_org = df_annotations_org.sort_values(['filename', 'start_time']).reset_index(drop=True)
    print(df_annotations_org)

    # Expand df_annotations_org with channel infos from hakan
    no_matches_counter = 0
    row_list_new = []
    for ix, row in df_annotations_org.iterrows():

        filename = row['filename']
        channel_ix = row['channel_ix']
        start_time = row['start_time']
        end_time = row['end_time']
        vocalization_type = row['vocalization_type']

        if vocalization_type == 'squeak':
    
            df_matching = df_hakan.loc[
                (df_hakan['filename'] == filename) &
                (df_hakan['start_time']-0.1 <= start_time) &
                (df_hakan['end_time']-3 >= end_time)
                #(df_hakan['start_time']-0.1 <= start_time) &
                #(df_hakan['end_time']-2 >= end_time)
                ].reset_index(drop=True)
            
            
            # #if(len(test.index) < 1):
            # if(len(df_matching.index) > 4):
            #     no_matches_counter += 1
            #     print(filename, channel_ix, start_time, end_time)
            #     print(df_matching)

            if(len(df_matching.index) > 1):
                # Get channel list
                channel_ixs = list(df_matching['channel_ix'].unique())
                if channel_ix not in channel_ixs:
                    no_matches_counter += 1
                    #print()
                    #print('Channel not matching', filename, channel_ix, start_time, end_time, channel_ixs)

                # Copy row and create new list of rows with missing channels
                #row_list = df_annotations_org.iloc[[ix]].values.tolist()
                row_list = df_annotations_org.iloc[[ix]].values.tolist()
                channel_ix_org = row_list[0][1]
                
                #print('channel_ix_org', channel_ix_org)
                for ix in channel_ixs:
                    if ix != channel_ix_org:
                        row_new = row_list[0].copy()
                        row_new[1] = ix
                        row_list_new.append(row_new)
                #print(row_list_new)

    #print('no_matches_counter', no_matches_counter)
 
    # Append extra channels rows            
    df_annotations_org = df_annotations_org.append(pd.DataFrame(row_list_new, columns=df_annotations_org.columns)).reset_index(drop=True)
    # Reorder
    df_annotations_org = df_annotations_org.sort_values(['filename', 'start_time', 'channel_ix']).reset_index(drop=True)
    #print(df_annotations_org[:20])
    print(df_annotations_org)
                
    # Create df_dilation (add time interval to start/end time)
    dilation_duration = 4.0
    df_dilation = df_annotations_org.copy()
    df_dilation['start_time'] = df_dilation['start_time'] - dilation_duration
    df_dilation['end_time'] = df_dilation['end_time'] + dilation_duration
    print(df_dilation)

    # Check if start_time >= 0 & end_time <= duration ?
    df_dilation.loc[df_dilation['start_time'] < 0.0, 'start_time'] = 0.0

    

    # Create df_merged for original annotations
    df_merged_list = {}
    df_merged_list['filename'] = []
    df_merged_list['start_time'] = []
    df_merged_list['end_time'] = []
    
    filename = df_dilation.filename.values[0]
    start_time = df_dilation.start_time.values[0]
    end_time = df_dilation.end_time.values[0]
    #print(filename, start_time, end_time)

    max_time_without_annotation = 2 #10 #10 #2 #4

    for ix, row in df_dilation.iterrows():
        
        if row['filename'] != filename or row['start_time'] - end_time > max_time_without_annotation:
            # Add current values to df_merged_list
            df_merged_list['filename'].append(filename)
            df_merged_list['start_time'].append(start_time)
            df_merged_list['end_time'].append(end_time)
            # Init new 
            filename = row['filename']
            start_time = row['start_time']
            end_time = row['end_time']
        else:
            end_time = row['end_time']

    # Add last row
    df_merged_list['filename'].append(filename)
    df_merged_list['start_time'].append(start_time)
    df_merged_list['end_time'].append(end_time)

    df_merged = pd.DataFrame.from_dict(df_merged_list)
    #print(df_merged)

    # Round times to nearest second
    df_merged['start_time'] = df_merged['start_time'].apply(np.floor)
    df_merged['end_time'] = df_merged['end_time'].apply(np.ceil)

    # Write audio parts and rename files according to annotation interval
    for ix, row in df_merged.iterrows():
        filename = row['filename']
        start_time = row['start_time'] # rounded to seconds
        end_time = row['end_time']
        
        filename_new = filename + create_postfix_str(start_time)
        df_merged.at[ix, 'filename_new'] = filename_new

        if write_audio_parts:
            path = src_dir + filename + '.wav'
            write_part_of_audio_file(path, start_time, end_time, dst_dir=dst_dir)

    
    print(df_merged)

    #quit()



    # Create df with annotation times relative to cuttet parts
    #df_new = df.copy()
    #df = df_hakan.copy()
    df = df_annotations_org.copy()
    #print(df)
    for ix, row in df.iterrows():
        filename = row['filename']
        channel_ix = row['channel_ix']
        start_time = row['start_time']
        end_time = row['end_time']
        #print(start_time.dtype)

        df_merged_row = df_merged.loc[
            (df_merged['filename'] == filename) &
            (df_merged['start_time'] <= start_time) &
            (df_merged['end_time'] >= end_time)
            ].reset_index(drop=True)
        
        assert len(df_merged_row.index) == 1

        filename_new = df_merged_row.at[0, 'filename_new']
        start_time_new = start_time - df_merged_row.at[0, 'start_time']
        end_time_new = end_time - df_merged_row.at[0, 'start_time']
        
        #print(filename, start_time, end_time, channel_ix,  filename_new, df_merged_row.at[0, 'start_time'], df_merged_row.at[0, 'end_time'], start_time_new, end_time_new)

        df.at[ix, 'filename'] = filename_new
        df.at[ix, 'start_time'] = start_time_new
        df.at[ix, 'end_time'] = end_time_new

    
    #print(df[['filename', 'channel_ix', 'start_time', 'end_time', 'vocalization_type']])


    # Additional infos
    # id_level, species_latin_name, annotator_name, 
    # record_date, record_filepath, recordist_name, 
    # equipment_name, equipment_sound_device, equipment_microphone,
    # location_name, location_habitat, location_lat, location_lng
    # collection_name

    df['id_level'] = 1
    df['species_latin_name'] = 'Scolopax rusticola'
    df['annotator_name'] = 'Frommolt, Karl-Heinz'
    df['recordist_name'] = 'Frommolt, Karl-Heinz'
    
    df['location_name'] = None
    df['record_date'] = None
    df['record_time'] = None

    df['collection_name'] = 'devise'

    df['record_filepath'] = None


    # Get location and date from filename
    for ix, row in df.iterrows():
        filename = row['filename']
        parts = filename.split('_')
        location_name = parts[0]
        df.at[ix, 'location_name'] = location_name
        time_str = None
        
        if location_name == 'Peenemuende':
            # Peenemuende_140525_327_4ch_S00055000ms 
            date_str = parts[1]
            
        else:
            # Schoenow_070401051656_S01146000ms, Schoenow_R4_1_090410040958_S01146000ms 
            date_str = parts[-2]
            time_str = date_str[6:]
            
            time_str = time_str[:2] + ':' + time_str[2:4] + ':' + time_str[4:6]
            
            # From Artenspektrum2007.xlsx recording time +1 hour for some recordings?
            #time_str = str(int(time_str[:2]) + 1).zfill(2) + ':' + time_str[2:4] + ':' + time_str[4:6]  
        
        data_str = '20' + date_str
        data_str = data_str[:4] + '-' + data_str[4:6] + '-' + data_str[6:8]
        #print(ix, parts, location_name, data_str, time_str)

        df.at[ix, 'record_date'] = data_str
        df.at[ix, 'record_time'] = time_str

        path_new = dst_dir + filename + '.wav'
        if not os.path.isfile(path_new): 
            print('Error: File not found', path_new)

        df.at[ix, 'record_filepath'] = path_new


    # Write metadata (excel, csv)
    if write_metadata:
        df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')
        #df.to_csv(metadata_path_without_ext + '.csv', index=False)


    print(df)

#process_hakan_schoenow()

def postprocess_hakan_arsu(year):

    write_audio_parts = False # True False
    write_metadata = True
    
    src_dir = root_dir + 'Annotationen/ARSU_temp/'
    #dst_dir = root_dir + 'Annotationen/_Segments/temp/'
    dst_dir = root_dir + 'Annotationen/_Segments/Scolopax_rusticola/'
    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_ARSU_' + str(year) + '_v07'

    # Collect annotations from excel files
    xlsx_files = [
        #"Scolopax_rusticola_Devise_ARSU_2021_v1.xlsx",
        #"Scolopax_rusticola_Devise_ARSU_2022_v1.xlsx",
        'Scolopax_rusticola_Devise_ARSU_' + str(year) + '_v1.xlsx'
    ]
    
    df_list = []
    for file in xlsx_files:
        path = src_dir + file

        if not os.path.isfile(path):
            print("Error: File not found", path)

        df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")
        df_list.append(df)
        print("n_rows", len(df))

    df = pd.concat(df_list).reset_index(drop=True)
    #print(df)

    # Get unique audio files
    files = list(df["filename"].unique())
    n_files = len(files)
    # print(files)
    print("n_files", n_files)



    # Create df_dilation (add time interval to start/end time)
    dilation_duration = 4.0
    df_dilation = df.copy()
    df_dilation['start_time'] = df_dilation['start_time'] - dilation_duration
    df_dilation['end_time'] = df_dilation['end_time'] + dilation_duration
    #print(df_dilation)

    # Check/correkt if start_time < 0 or end_time > duration
    #df_dilation.loc[df_dilation['start_time'] < 0.0, 'start_time'] = 0.0
    for ix, row in df_dilation.iterrows():
        if row['start_time'] < 0.0:
            df_dilation.at[ix, 'start_time'] = 0.0
            print(row['filename'], 'start_time < 0.0,', row['start_time'], '-->', df_dilation.at[ix, 'start_time'])
        # Get duration
        path = src_dir + 'Scolopax_rusticola_Devise_ARSU_' + str(year) + '/' + row['filename'] + '.flac'
        with sf.SoundFile(path) as f:
            duration = f.frames/f.samplerate
        if row['end_time'] > duration:
            df_dilation.at[ix, 'end_time'] = duration
            print(row['filename'], 'end_time > duration,', row['end_time'], '-->', df_dilation.at[ix, 'end_time'] )
    
    #quit()

    # Create df_merged for original annotations
    df_merged_list = {}
    df_merged_list['filename'] = []
    df_merged_list['start_time'] = []
    df_merged_list['end_time'] = []
    
    filename = df_dilation.filename.values[0]
    start_time = df_dilation.start_time.values[0]
    end_time = df_dilation.end_time.values[0]
    #print(filename, start_time, end_time)

    max_time_without_annotation = 2 #10 #2 #4

    for ix, row in df_dilation.iterrows():

        if row['filename'] != filename or row['start_time'] - end_time > max_time_without_annotation:
            # Add current values to df_merged_list
            df_merged_list['filename'].append(filename)
            df_merged_list['start_time'].append(start_time)
            df_merged_list['end_time'].append(end_time)
            # Init new 
            filename = row['filename']
            start_time = row['start_time']
            end_time = row['end_time']
        else:
            end_time = row['end_time']

    # Add last row
    df_merged_list['filename'].append(filename)
    df_merged_list['start_time'].append(start_time)
    df_merged_list['end_time'].append(end_time)

    df_merged = pd.DataFrame.from_dict(df_merged_list)
    #print(df_merged)
            


    # Round times to nearest second
    df_merged['start_time'] = df_merged['start_time'].apply(np.floor)
    df_merged['end_time'] = df_merged['end_time'].apply(np.ceil)

    # Write audio parts and rename files according to annotation interval
    for ix, row in df_merged.iterrows():
        filename = row['filename']
        start_time = row['start_time'] # rounded to seconds
        end_time = row['end_time']
        
        filename_new = filename + create_postfix_str(start_time) + '_c0'
        df_merged.at[ix, 'filename_new'] = filename_new

        if write_audio_parts:
            path = src_dir + 'Scolopax_rusticola_Devise_ARSU_' + str(year) + '/' + filename + '.flac'
            print('Writing', filename_new)
            write_part_of_audio_file(path, start_time, end_time, channel_ix=0, dst_dir=dst_dir, format='wav')

    
    #print(df_merged)
    n_files_merged = len(df_merged)
    print('n_files_merged', n_files_merged)

    #quit()

    # Create df with annotation times relative to cuttet parts

    #print(df)
    for ix, row in df.iterrows():
        filename = row['filename']
        channel_ix = row['channel_ix']
        start_time = row['start_time']
        end_time = row['end_time']
        #print(start_time.dtype)

        df_merged_row = df_merged.loc[
            (df_merged['filename'] == filename) &
            (df_merged['start_time'] <= start_time) &
            (df_merged['end_time'] >= end_time)
            ].reset_index(drop=True)
        
        assert len(df_merged_row.index) == 1

        filename_new = df_merged_row.at[0, 'filename_new']
        start_time_new = start_time - df_merged_row.at[0, 'start_time']
        end_time_new = end_time - df_merged_row.at[0, 'start_time']
        
        #print(filename, start_time, end_time, channel_ix,  filename_new, df_merged_row.at[0, 'start_time'], df_merged_row.at[0, 'end_time'], start_time_new, end_time_new)

        df.at[ix, 'filename'] = filename_new
        df.at[ix, 'start_time'] = start_time_new
        df.at[ix, 'end_time'] = end_time_new

        # Add file path
        df.at[ix, 'record_filepath'] = dst_dir + filename_new + '.wav'


    # Add channel info
    df['channel_ix'] = 0
    # Add id_level=1 (Tim knows)
    df['id_level'] = 1
    # Correct time format (e.g. 21-28-11 --> 21:28:11)
    df['record_time'] = df['record_time'].str.replace('-',':')

    # Add recording equipment info
    df['equipment_name'] = 'devise'


    # Rename cols
    df = df.rename(columns={"quality": "quality_tag"})
    df = df.rename(columns={"has_background": "background_level"})
    df = df.rename(columns={"comment": "remarks"})

    # Correct some mistakes
    df.loc[df['vocalization_type'] == '3', 'vocalization_type'] = 'grunt'
    df.loc[df['vocalization_type'] == 'sgr', 'vocalization_type'] = 'grunt'
    

    # Correct start/end freq (Tim only annotated time intervals!)
    df.loc[df['vocalization_type'] == 'grunt', 'start_frequency'] = 200.0
    df.loc[df['vocalization_type'] == 'grunt', 'end_frequency'] = 2500.0 # 2000/2500
    df.loc[df['vocalization_type'] == 'squeak', 'start_frequency'] = 1500.0 # 1500/2000
    df.loc[df['vocalization_type'] == 'squeak', 'end_frequency'] = None # 24000.0/NF/None
    
    print(df)



    # Write metadata (excel, csv)
    if write_metadata:
        df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')
        #df.to_csv(metadata_path_without_ext + '.csv', index=False)

#postprocess_hakan_arsu(2021)
#postprocess_hakan_arsu(2022)

def process_Lars_Annotations():

    write_metadata = True
    
    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/CrexCrex_LarsAnnotaions_v03'

    df_list = []

    # Search for audacity label track txt files
    #root_src_dir = lars_dir + 'Criewen_2022_05_15/'
    #root_src_dir = lars_dir + 'Unteres_Odertal_2021_06_10/'
    #root_src_dir = lars_dir + 'Unteres_Odertal_2021_06_16/'
    #root_src_dir = lars_dir + 'Unteres_Odertal_2021_06_23/'
    #root_src_dir = lars_dir + 'Unteres_Odertal_2021_07_15/'
    #root_src_dir = lars_dir + 'Crex_crex Tierstimmenarchiv'

    # All Lars Annotations
    root_src_dir = lars_dir
    
    n_files = 0
    for root, dirs, files in os.walk(root_src_dir):
        for file in files:
            # Only use txt file with corresponing wav file
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                path_wav = path[:-4] + '.wav'
                if os.path.isfile(path_wav): 
                    print(path)
                    df = read_audacity_label_file(path, ignore_freq_range=True)
                    #if df is not None:
                    df = process_audacity_label_data(df, check_label_data=False)

                    # Add filename, record_filepath
                    df['record_filepath'] = path_wav
                    df['filename'] = os.path.splitext(os.path.basename(path_wav))[0]
                    #print(df)

                    df_list.append(df)
                else:
                    print('Warning no corresponding wav file', path)
            
            n_files += 1
    
    
    # Concat and sort
    df = pd.concat(df_list).reset_index(drop=True)
    df = df.sort_values(['filename', 'start_time']).reset_index(drop=True)

    # Move filename to front
    df.insert(0, 'filename', df.pop('filename'))

    print(df)

    # Check distinct species/bg events
    species_unique = list(df["species"].unique())
    print('species_unique', species_unique) # ['Crex crex BG', 'wind', 'Crex crex']

    # Postprocess annotations

    # Rename cols
    df = df.rename(columns={"species": "species_latin_name"})
    df = df.rename(columns={"call_type": "vocalization_type"})
    df = df.rename(columns={"quality": "quality_tag"})
    df = df.rename(columns={"comment": "remarks"})

    # Add cols
    df['record_date'] = None
    df['record_time'] = None
    df['location_name'] = None
    df['noise_name'] = None
    df['annotator_name'] = 'Beck, Lars'
    df['recordist_name'] = 'Frommolt, Karl-Heinz'
    df['collection_name'] = 'devise'

    # Add infos
    for ix, row in df.iterrows():
        filename = row['filename']
        species = row['species_latin_name']

        filename_parts = filename.split('_')

        if filename.startswith('CRIEWEN'):
            df.at[ix, 'location_name'] = 'Criewen'
            df.at[ix, 'record_date'] = filename_parts[1][:4] + '-' + filename_parts[1][4:6] + '-' + filename_parts[1][6:8]
            df.at[ix, 'record_time'] = filename_parts[2][:2] + ':' + filename_parts[2][2:4] + ':' + filename_parts[2][4:6]

        if filename.startswith('Devise'):
            df.at[ix, 'location_name'] = 'Unteres Odertal'
            df.at[ix, 'record_date'] = filename_parts[1][:10]
            df.at[ix, 'record_time'] = filename_parts[1][11:19].replace("-", ":")

        if species != 'Crex crex':
            df.at[ix, 'species_latin_name'] = None
            if species == 'Crex crex BG':
                df.at[ix, 'noise_name'] = 'Crex crex absent'
            else:
                df.at[ix, 'noise_name'] = species
                print(ix, filename, species)


    # Correct vocalization_type = s --> song
    df.loc[df['vocalization_type'] == 's', 'vocalization_type'] = 'song'
    
    
    # Write metadata (excel, csv)
    if write_metadata:
        df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

#process_Lars_Annotations()


print('Done.')