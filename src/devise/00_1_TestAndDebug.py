import os
import numpy as np
import soundfile as sf

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
path = src_dir + 'Devise03_2021-05-31T21-24-55.flac'
#path = src_dir + 'Devise04_2021-05-21T22-01-03_VP4_2_2.flac'
read_and_process_flac_files(path)

print('Done.')