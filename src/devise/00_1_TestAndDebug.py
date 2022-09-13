import os
import numpy as np
import soundfile as sf
import pandas as pd

root_dir = '/mnt/z/Projekte/DeViSe/'

def read_and_process_flac_files(path):

    if not os.path.isfile(path): 
        print('Error: File not found', path)

    
    with sf.SoundFile(path) as f:
		#print(f)
		#print(f.extra_info)
        samplerate = f.samplerate
        n_channels = f.channels
        n_frames = len(f)
        duration = n_frames/samplerate
        subtype = f.subtype # BitDepth
        print('samplerate', samplerate, 'n_channels', n_channels, 'n_frames', n_frames, 'duration', duration, 'subtype', subtype)
		

    audio_data, samplerate = sf.read(path, always_2d=True)
    print(audio_data.shape)
    print(np.mean(audio_data[:,0]), np.max(audio_data[:,0]))

    # Save first channel
    # ToDo maybe remove dc offset, normalize, hp filter ?
    channel_ix = 0
    #filename_without_ext = os.path.splitext(os.path.basename(path))[0]
    path_new = path[:-5] + '_c' + str(channel_ix) + '.wav'
    #sf.write(path_new, audio_data[:,channel_ix], samplerate, subtype)

src_dir = root_dir + 'Annotationen/ARSU_temp/Scolopax_rusticola_Devise_ARSU_2021/'
#path = src_dir + 'Devise03_2021-05-31T21-24-55.flac'
#path = src_dir + 'Devise04_2021-05-21T22-01-03_VP4_2_2.flac'
path = src_dir + 'Devise07_2021-06-17T22-44-13.flac'
#path = root_dir + 'Annotationen/ARSU_temp/Scolopax_rusticola_Devise_ARSU_2022/Devise03_2022-06-02T22-02-00.flac'
path = root_dir + 'Annotationen/ARSU_temp/Scolopax_rusticola_Devise_ARSU_2022/Devise10_2022-05-25T20-58-22.flac'

#read_and_process_flac_files(path)

def parse_date_in_filename(path):

    # AMMOD style (new)
    #filename_without_ext = os.path.splitext(os.path.basename(path))[0]
    filename = os.path.basename(path)
    parts = filename.split('_')
    print(parts)
    for part in parts:
        if len(part) == 8 and part[:2] == '20':
            print('date string', part)
    

#path = '/mnt/z/Projekte/AMMOD/AudioData/BRITZ01/BRITZ01_201903/BRITZ01_190313_104500.wav'
path = '/mnt/z/Projekte/AMMOD/AudioData/BRITZ01/BRITZ01_202206/BRITZ01_20220601_000000.wav'
#parse_date_in_filename(path)

def replaceNegativValuesInDataframeCol():

    df = pd.DataFrame({"A": [1, 2, -3, 4, -5, 6],
                   "B": [3, -5, -6, 7, 3, -2],
                   "C": [-4, 5, 6, -7, 5, 4],
                   "D": [34, 5, 32, -3, -56, -54]})
  
    print(df)

    
    df.loc[df['A'] < 0, 'A'] = 0
    print(df)

#replaceNegativValuesInDataframeCol()


def getOpenIntervals():

    # https://stackoverflow.com/questions/71784063/how-to-correctly-find-intervals-between-other-intervals
    
    global_start_time = 0.0
    global_end_time = 12.0
    
    df_dict = {}
    df_dict['start_time'] = []
    df_dict['end_time'] = []

    df_new_dict = {}
    df_new_dict['start_time'] = []
    df_new_dict['end_time'] = []

    df_dict['start_time'].append(1.0)
    df_dict['end_time'].append(2.0)
    df_dict['start_time'].append(1.0)
    df_dict['end_time'].append(4.0)
    df_dict['start_time'].append(2.0)
    df_dict['end_time'].append(3.0)
    df_dict['start_time'].append(5.0)
    df_dict['end_time'].append(8.0)
    df_dict['start_time'].append(9.0)
    df_dict['end_time'].append(10.0)

    df = pd.DataFrame.from_dict(df_dict)
    print(df)

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
    if global_end_time > start_time:
        df_new_dict['start_time'].append(start_time)
        df_new_dict['end_time'].append(global_end_time)

    # Convert to df
    df_new = pd.DataFrame.from_dict(df_new_dict)
    print(df_new)

#getOpenIntervals()

def checScolopaxRusticolaCallTypesFreq():

    from mysql.connector import connect
    import matplotlib.pyplot as plt

    db = {'host': 'localhost', 'user': 'root', 'port': 3306, 'password': 'Password123!?', 'name': 'libro_animalis'}
    db_connection = connect(host=db['host'], port=db['port'], user=db['user'], passwd=db['password'], database=db['name'], auth_plugin='mysql_native_password',)
    
    with db_connection.cursor(dictionary=True) as db_cursor:

        #query = 'SELECT * FROM libro_animalis.annotation_view LIMIT 4;'
        #query = "SELECT * FROM libro_animalis.annotation_view WHERE collection LIKE '%devise%' AND annotator LIKE 'Steinkamp%' AND vocalization_type = 'squeak';"
        
        query = "SELECT * FROM libro_animalis.annotation_view WHERE " 
        query += "(vocalization_type = 'squeak' "
        query += "OR vocalization_type = 'grunt') "
        query += "AND start_frequency IS NOT NULL "
        query += ";"
        
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        print('n_rows', db_cursor.rowcount)

        events = []
        squeak_start_freq = []
        squeak_end_freq = []
        grunt_start_freq = []
        grunt_end_freq = []
        for row in rows:
            start_frequency = float(row['start_frequency'])
            end_frequency = float(row['end_frequency'])
            vocalization_type = row['vocalization_type']
            event = {
                'annotator': row['annotator'],
                'vocalization_type':  vocalization_type, 
                'start_frequency': start_frequency,
                'end_frequency': end_frequency
                }
            if vocalization_type == 'squeak':
                squeak_start_freq.append(start_frequency)
                squeak_end_freq.append(end_frequency)
            if vocalization_type == 'grunt':
                grunt_start_freq.append(start_frequency)
                grunt_end_freq.append(end_frequency)

            print(len(events), event)
            events.append(event)

        print(np.max(squeak_end_freq))
        plt.plot(squeak_start_freq, squeak_end_freq, 'o')
        plt.plot(grunt_start_freq, grunt_start_freq, 'o')
        plt.xlim([0, 23000])
        plt.ylim([0, 23000])
        
        plt.savefig('src/devise/images/test02.jpg', bbox_inches='tight')
        #plt.show()


checScolopaxRusticolaCallTypesFreq()

print('Done.')