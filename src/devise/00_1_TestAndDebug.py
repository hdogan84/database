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

replaceNegativValuesInDataframeCol()


print('Done.')