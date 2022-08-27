# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import numpy as np
import pandas as pd
import soundfile as sf

root_dir = '/mnt/z/Projekte/DeViSe/'
metadata_dir = root_dir + 'Annotationen/'
lars_dir = '/mnt/z/AG/TSA/Lars_Beck/'


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

def process_audacity_label_data(df):

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
    key_names = ['species', 'call_type', 'quality', 'id_level', 'has_background', 'comment']

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


path = lars_dir + 'Unteres_Odertal_2021_06_10/Devise02_2021-06-10T22-38-32_Pos01.txt'
#path = metadata_dir + '_BackupML/Devise07_2022-05-09T20-40-27_Annotation.txt'
path = lars_dir + 'Criewen_2022_05_15/Criewen02/CRIEWEN02_20220515_202400.txt'
#df = read_audacity_label_file(path)
#if df: df = process_audacity_label_data(df)

def read_raven_label_file(path):

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    # Read audacity label track txt file
    df = pd.read_csv(path, sep='\t')
    #print(df)
    return df

path = root_dir + 'Scolopax_rusticola_Recordings/Monitoring/Peenemuende_140525_327_4ch.Table.1.selections.txt'
#read_raven_label_file(path)

def write_part_of_audio_file(path, start_time, end_time, channel_ix=None, dst_dir=None):

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

        path_new = dst_dir + filename_new + ext

        if channel_ix is not None:
            sf.write(path_new, data[:,channel_ix], samplerate, subtype=subtype)
        else:
            sf.write(path_new, data, samplerate, subtype=subtype)
        
    else:
        print('Error file not found', path)

    
    

def process_Criewen_2022_05_15():

    df_list = []

    # Search for audacity label track txt files
    root_src_dir = lars_dir + 'Criewen_2022_05_15/'

    #root_src_dir = metadata_dir + 'Unteres_Odertal_2021_06_10/'
    #root_src_dir = metadata_dir + 'Unteres_Odertal_2021_06_16/'
    #root_src_dir = metadata_dir + 'Unteres_Odertal_2021_06_23/'
    #root_src_dir = metadata_dir + 'Unteres_Odertal_2021_07_15/'
    
    for root, dirs, files in os.walk(root_src_dir):
        for file in files:
            # Only use txt file with corresponing wav file
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                path_wav = path[:-4] + '.wav'
                if os.path.isfile(path_wav): 
                    print(path)
                    df = read_audacity_label_file(path, ignore_freq_range=True)
                    if df is not None:
                        df = process_audacity_label_data(df)
                        df_list.append(df)
                else:
                    print('Warning no corresponding wav file', path)

#process_Criewen_2022_05_15()

def process_Crex_crex_Unteres_Odertal_2017():

    # ToDo: df_new_dict in new format, save metadata like schoenow and maybe separate for Crex crex vs BG

    write_audio_files = True # True False

    audio_root_src_dir = root_dir + 'Crex_crex_annotated/Crex_crex_Unteres_Odertal_2017_annotated/'
    audio_root_dst_dir = root_dir + 'Annotationen/_Segments/'
    
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
    keys = ['filename', 'class', 'collection_id', 'channel_ix', 'start_time', 'end_time', 'sub_dir']
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
            class_new = 'Crex_crex'
        if row['class'] == 'BG':
            class_new = 'Crex_crex_BG'

        path = audio_root_src_dir + row['sub_dir'] + '/' + filename + '.wav'
        
        if os.path.isfile(path):
            
            if write_audio_files:
                dst_dir = audio_root_dst_dir + class_new + '/'
                write_part_of_audio_file(path, start_time, end_time, channel_ix=channel_ix, dst_dir=dst_dir)


            filename_new = filename + create_postfix_str(start_time) + '_c' + str(channel_ix)

            df_new_dict['filename'].append(filename_new + '.wav')
            df_new_dict['class'].append(class_new)
            df_new_dict['collection_id'].append(row['collection_id'])
            df_new_dict['channel_ix'].append(None)
            df_new_dict['start_time'].append(None)
            df_new_dict['end_time'].append(None)
            df_new_dict['sub_dir'].append(None)

            print(filename, filename_new)


        else:
            print('Missing', path)

    df_new = pd.DataFrame.from_dict(df_new_dict)
    print(df_new)

    excel_path = audio_root_dst_dir + 'test02.xlsx'
    df_new.to_excel(excel_path, index=False, engine='openpyxl')  

process_Crex_crex_Unteres_Odertal_2017()

def fva_test():

    # Read excel file
    path = metadata_dir + 'Scolopax_rusticola_FVA_BadenWürttemberg/220722_fva_selections.csv'

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    #encoding = 'cp1252'
    encoding = 'ISO-8859-1'
    df = pd.read_csv(path, sep=';', encoding=encoding)
    print(df.columns.values.tolist())
    
    # Drop cols not used (yet)
    df = df.drop(columns=['Unnamed: 0', 'deploy_id', 'dateiname', 'selection', 'view', 'channel', 'species_code', 'common_name', 'import'])

    # Sort by (new) file name and begin_time
    df = df.sort_values(['new_name', 'begin_time'])

    print(df[10:30])

#fva_test()

def process_hakan_schoenow():

    write_audio_parts = False # True False
    write_metadata = False
    
    src_dir = root_dir + 'Scolopax_rusticola_Recordings/Monitoring/'
    dst_dir = root_dir + 'Annotationen/_Segments/Scolopax_rusticola/'
    metadata_path_without_ext =  root_dir + 'Annotationen/_MetadataReadyForDbInsert/Scolopax_rusticola_MfN_Peenemuende+Schoenow_v01'

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

    
    # Create merged table
    df_merged_list = []

    df_merged_list = {}
    df_merged_list['filename'] = []
    df_merged_list['start_time'] = []
    df_merged_list['end_time'] = []
    
    filename = df.filename.values[0]
    start_time = df.start_time.values[0]
    end_time = df.end_time.values[0]
    #print(filename, start_time, end_time)

    max_time_without_annotation = 2 #4

    for ix, row in df.iterrows():
        
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

    # Rename files according to annotation interval
    for ix, row in df_merged.iterrows():
        filename_new = row['filename'] + create_postfix_str(row['start_time'], row['end_time'])
        df_merged.at[ix, 'filename_new'] = filename_new
    
    print(df_merged)

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
        df.loc[df['vocalization_type'] == 1, 'vocalization_type'] = 'sq'
        df.loc[df['vocalization_type'] == 2, 'vocalization_type'] = 'gr'
        
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

        if vocalization_type == 'sq':
    
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
    dilation_time = 4
    df_dilation = df_annotations_org.copy()
    df_dilation['start_time'] = df_dilation['start_time'] - dilation_time
    df_dilation['end_time'] = df_dilation['end_time'] + dilation_time
    print(df_dilation)

    

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
        df.to_csv(metadata_path_without_ext + '.csv', index=False)


    print(df)

#process_hakan_schoenow()

print('Done.')