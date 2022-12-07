'''
# Prepare birdid-europe254-2103 on MFN0470
(docker load -i /net/mfnstore-lin/export/tsa_transfer/Backups/DockerImages/birdid-europe254-2103-flask-v04.tar)
DATA=/net/mfnstore-lin/export/tsa_transfer
docker run -p 4000:4000 --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 -v $DATA:/mnt --ipc=host -it --name soundid --rm birdid-europe254-2103-flask-v04 /bin/bash
# Edit SegmentOverlapForTestFilesInPerc = 0 (statt 60)
apt-get update
apt-get install nano
nano config.py (nano predictSingleFile.py)
# Run flask
python flaskApp.py


'''

import os
import numpy as np
import pandas as pd
import soundfile as sf
import requests
#import pickle
import pickle5 as pickle # conda install -c conda-forge pickle5
from sklearn.metrics import average_precision_score



root_dir = '/mnt/z/Projekte/DeViSe/'
metadata_dir = root_dir + 'Annotationen/'



def get_birdid_results():

    root_dir_audio = '/net/mfnstore-lin/export/tsa_transfer/TrainData/libro_animalis/original/'
    root_dir_audio_within_docker = '/mnt/TrainData/libro_animalis/original/'

    # Prepare params for birdid
    url = 'http://localhost:4000/identify'
    params = {
        'path': '/mnt/TrainData/PyTorch/Jobs/BirdId1907Europe254/12_1_ReDoWithSedModel/ProductionReady/TestFiles/FriCoe00001.wav',
        'outputStyle': 'resultDict', # old param version
        #'outputDir': '/mnt/Results/birdid-europe254-2103/devise/221112_2_TestSet_CrexCrex'
        #'outputDir': '/mnt/Results/birdid-europe254-2103/devise/221113_1_TestSet_ScolopaxRusticola'
        'outputDir': '/mnt/Results/birdid-europe254-2103/devise/221114_1_TestSet_ScolopaxRusticolaFVA'
        }

    # Test
    # params['path'] = '/mnt/TrainData/PyTorch/Jobs/BirdId1907Europe254/12_1_ReDoWithSedModel/ProductionReady/TestFiles/AcrSci00001.wav'
    # res = requests.get(url, params=params)
    # print(res.json())


    # Load test set excel file
    #path = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v04_5s_TestSplit.xlsx'
    #path = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaAnnotations_v24_5s_TestSplit.xlsx'
    path = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaFVA_v04_5s_TestSplit.xlsx'
    df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")
    #print(df)

    # Get unique audio files
    files = list(df['filename'].unique())
    n_files = len(files)
    print("n_files", n_files) # 228 for Crex crex, 1143 for Scolopax rusticola

    for ix in range(n_files):

        #if ix > 1: break

        filename = files[ix]
        # Get subdir from first entry with filename
        df_filename = df[df['filename']==filename].reset_index(drop=True)
        subdir = df_filename.file_path.values[0]

        print(ix, subdir, filename)

        path = root_dir_audio + subdir + '/' + filename
        path_within_docker = root_dir_audio_within_docker + subdir + '/' + filename

        if not os.path.isfile(path): 
            print('Error: File not found', path)

        # Adjust path param for birdid request
        params['path'] = path_within_docker

        # birdid inference 
        res = requests.get(url, params=params)
        #print(res.json())

#get_birdid_results()

def process_birdid_results():

    # Crex crex
    path = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v14_5s_TestSplit.xlsx'
    root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/devise/221112_2_TestSet_CrexCrex/'
    class_ix = 36

    # # Scolopax rusticola
    # path = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaAnnotations_v24_5s_TestSplit.xlsx'
    # root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/devise/221113_1_TestSet_ScolopaxRusticola/'
    # class_ix = 131

    # # Scolopax rusticola FVA
    # path = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaFVA_v04_5s_TestSplit.xlsx'
    # root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/devise/221114_1_TestSet_ScolopaxRusticolaFVA/'
    # class_ix = 131


    channel_pooling = 'max'

    # Load test set excel file
    df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")

    # Convert times using 3 decimals to prevent rounding errors
    df[["start_time", "end_time"]] = df[["start_time", "end_time"]].applymap('{:.3f}'.format)

    # Add target col (1: species, 0: not species)
    df['target'] = 1
    df.loc[df['species_latin_name'] == '', 'target'] = 0

    # Add prob col
    df['birdid-europe254'] = 0.0
    
    #print(df.dtypes)
    print(df[11180:11190])

    # Get unique audio files
    files = list(df['filename'].unique())
    n_files = len(files)
    print("n_files", n_files) # 228 for Crex crex, 1143 for Scolopax rusticola

    targets = []
    probs = []

    for file_ix in range(n_files):

        #if file_ix > 1: break

        filename = files[file_ix]
        
        # Read pkl file
        #path = 
        path = root_dir_pkl + filename[:-4] + '.pkl'
        result_dict = pickle.load(open(path,'rb'))
        #print(result_dict.keys()) # 'fileId', 'modelId', 'segmentDuration', 'classIds', 'classNamesScientific', 'startTimes', 'probs'
        predictions = result_dict['probs']

        if channel_pooling == 'max':
            predictions = np.max(predictions, axis=0)
        if channel_pooling == 'mean':
            predictions = np.mean(predictions, axis=0)


        print(file_ix, filename[:-4], predictions.shape)
        #print(result_dict['startTimes'])

        for start_time in result_dict['startTimes']:

            # Get corresponding df row
            #row = df.loc[(df['filename'] == filename) & (df['start_time'] == '{:.3f}'.format(start_time))]
            row_ixs = list(df.index[(df['filename'] == filename) & (df['start_time'] == '{:.3f}'.format(start_time))])
            
            # Check if start_time always corresponds with one df row
            #assert len(row_ixs) == 1
            if len(row_ixs) != 1: 
                print('Warning no match', file_ix, start_time, '{:.3f}'.format(start_time), row_ixs)
            else:
            
                row_ix = row_ixs[0]

                target = df.at[row_ix, 'target']
                segm_ix = result_dict['startTimes'].index(start_time)
                prob = predictions[segm_ix,class_ix]

                df.at[row_ix, 'birdid-europe254'] = prob

                targets.append(target)
                probs.append(prob)

                #print(file_ix, filename[:-4], start_time, target, prob)

    # Get metrics
    average_precision = average_precision_score(targets, probs, average='micro') # average egal micro=macro=samples 
    print('average_precision', average_precision)

    # Crex crex:                0.9743679871082258  --> 0.9956393921753952 after checking/correcting false positives       
    # Scolopax rusticola:       0.8943062156793132
    # Scolopax rusticola FVA:   0.8252411107201116

    # Reconvert times
    #df[["start_time", "end_time"]] = df[["start_time", "end_time"]].astype(float)

    # Save to excel
    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v05'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

            
#process_birdid_results()

def process_birdnet_results():

    # Crex crex
    path = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v15_5s_Scores.xlsx'
    root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdnet-public-3k-v2.2/devise/221112_2_TestSet_CrexCrex/'
    class_ix = 863

    # # Scolopax rusticola
    # path = metadata_dir + '_MetadataTestSets/ScolopaxRusticolaAnnotations_v25_5s_Scores.xlsx'
    # root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdnet-public-3k-v2.2/devise/221113_1_TestSet_ScolopaxRusticola/'
    # class_ix = 2736

    channel_pooling = 'max'
    segment_pooling = 'max'

    # Load test set excel file
    df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")

    # Convert times using 3 decimals to prevent rounding errors
    #df[["start_time", "end_time"]] = df[["start_time", "end_time"]].applymap('{:.3f}'.format)

    # Add target col (1: species, 0: not species)
    #df['target'] = 1
    #df.loc[df['species_latin_name'] == '', 'target'] = 0

    # Add prob col
    df['birdnet-public-3k-v2.2'] = 0.0

    # Get unique audio files
    files = list(df['filename'].unique())
    n_files = len(files)
    print("n_files", n_files) # 228 for Crex crex, 1143 for Scolopax rusticola

    targets = []
    probs = []

    for file_ix in range(n_files):

        #if file_ix > 1: break

        filename = files[file_ix]
        
        # Read pkl file
        path = root_dir_pkl + filename[:-4] + '.pkl'
        result_dict = pickle.load(open(path,'rb'))
        #print(result_dict.keys()) # 'modelName', 'version', 'file_id', 'n_channels', 'n_segments', 'n_classes', 'segment_duration', 'class_ids_birdnet', 'class_ids', 'start_times', 'prediction_logits', 'prediction_probabilities'
        predictions = result_dict['prediction_probabilities']

        if channel_pooling == 'max':
            predictions = np.max(predictions, axis=0)
        if channel_pooling == 'mean':
            predictions = np.mean(predictions, axis=0)

        print(file_ix, filename[:-4], predictions.shape)
        #print(result_dict['start_times'])


        # Create dataframe of prediction start/end times
        start_times = result_dict['start_times']
        end_times = [x+3.0 for x in start_times]
        df_prediction_intervals = pd.DataFrame(list(zip(start_times, end_times)), columns =['start_time', 'end_time'])
        #print(df_prediction_intervals)

        # Iterate over target intervals of file and collect predictions fitting in target interval
        df_filename = df[df['filename']==filename].reset_index(drop=True)
        #print(df_filename)
        
        for ix, row in df_filename.iterrows():
            pred_ixs = list(df_prediction_intervals.index[
                (df_prediction_intervals['start_time'] >= row['start_time']) &
                (df_prediction_intervals['end_time'] <= row['end_time'])
                ])
            
            preds = predictions[pred_ixs, class_ix]
            if segment_pooling == 'max':
                pred = np.max(preds, axis=0)
            if segment_pooling == 'mean':
                pred = np.mean(preds, axis=0)
            
            #print(ix, row['start_time'], row['end_time'], pred_ixs, pred.shape)
            #print(file_ix, filename[:-4], ix, row['start_time'], row['end_time'], row['target'], pred)

            targets.append(row['target'])
            probs.append(pred)

            #df.at[ix, 'birdnet-public-3k-v2.2'] = pred
            df.loc[(df['filename'] == filename) & (df['start_time'] == row['start_time']), 'birdnet-public-3k-v2.2'] = pred

    # Get metrics
    average_precision = average_precision_score(targets, probs, average='micro') # average egal micro=macro=samples 
    print('average_precision', average_precision)

    # Crex crex:                0.9793124516105638  (birdid: 0.9743679871082258)
    # Crex crex new:            0.9902080338822844  (birdid: 0.9956393921753952)
    # Scolopax rusticola:       0.8941700432623295  (birdid: 0.8943062156793132)

    # Save to excel
    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/_temp_v06'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

process_birdnet_results()

def get_crex_crex_false_positive_intervals():

    # Get all crex crex false positive intervals to check if actually true positive
    
    path = metadata_dir + '_MetadataTestSets/CrexCrexAnnotations_v05_5s_Scores.xlsx'
    df = pd.read_excel(path, keep_default_na=False, engine="openpyxl")
    
    # Remove cols
    df = df.drop(columns=['quality_tag', 'background_level', 'file_path', 'filename', 'duration', 'channels', 'species_latin_name', 'split'])

    # Filter false positives
    min_confidence = 0.3
    df = df.loc[
        (df['target'] == 0) &
        (df['birdid-europe254'] > min_confidence)
        ].reset_index(drop=True)

    df = df.drop(columns=['target'])
    
    print(df)

    # Save to excel
    metadata_path_without_ext = metadata_dir + '_MetadataTestSets/CrexCrexFalsePositivesToCheck_v01'
    df.to_excel(metadata_path_without_ext + '.xlsx', index=False, engine='openpyxl')

#get_crex_crex_false_positive_intervals()

def get_more_crex_crex_birdid_results():

    # Get results from files not in db or official test set yet

    # Devise recordings without Crex crex
    audio_src_dir = '/net/mfnstore-lin/export/tsa_transfer/AudioData/Devise_TestSets/Crex_crex_absent/'
    audio_src_dir_within_docker = '/mnt/AudioData/Devise_TestSets/Crex_crex_absent/'

    # Devise recordings with weak Crex crex
    audio_src_dir = '/net/mfnstore-lin/export/tsa_transfer/AudioData/Devise_TestSets/Crex_crex_weak/'
    audio_src_dir_within_docker = '/mnt/AudioData/Devise_TestSets/Crex_crex_weak/'

    # Prepare params for birdid
    url = 'http://localhost:4000/identify'
    params = {
        'path': '/mnt/TrainData/PyTorch/Jobs/BirdId1907Europe254/12_1_ReDoWithSedModel/ProductionReady/TestFiles/FriCoe00001.wav',
        'outputStyle': 'resultDict', # old param version
        #'outputDir': '/mnt/Results/birdid-europe254-2103/devise/221116_1_TestSet_CrexCrexAbsent'
        'outputDir': '/mnt/Results/birdid-europe254-2103/devise/221116_1_TestSet_CrexCrexWeak'
        }

    files = os.listdir(audio_src_dir)
    for file in files:
        print(file)
        path_within_docker = audio_src_dir_within_docker + file

        # Adjust path param for birdid request
        params['path'] = path_within_docker

        # birdid inference 
        res = requests.get(url, params=params)

#get_more_crex_crex_birdid_results()

def process_more_crex_crex_birdid_results():

    import matplotlib.pyplot as plt

    root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/devise/221116_1_TestSet_CrexCrexAbsent/'
    #root_dir_pkl = '/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/devise/221116_1_TestSet_CrexCrexWeak/'
    class_ix = 36

    channel_pooling = 'max'

    files = os.listdir(root_dir_pkl)
    for file in files:
        #print(file)

        path = root_dir_pkl + file
        result_dict = pickle.load(open(path,'rb'))
        #print(result_dict.keys()) # 'fileId', 'modelId', 'segmentDuration', 'classIds', 'classNamesScientific', 'startTimes', 'probs'
        predictions = result_dict['probs']

        if channel_pooling == 'max':
            predictions = np.max(predictions, axis=0)
        if channel_pooling == 'mean':
            predictions = np.mean(predictions, axis=0)
        
        # Filter class
        predictions = predictions[:,class_ix]

        print(file, np.max(predictions))

        # Plot


        # plt.plot(squeak_start_freq, squeak_end_freq, 'o')
        # plt.plot(grunt_start_freq, grunt_start_freq, 'o')
        # #plt.xlim([0, 23000])
        # #plt.ylim([0, 23000])
        
        #plt.bar(result_dict['startTimes'], predictions, color='#7f6d5f', width=barWidth, edgecolor='white', label='var1')
        plt.bar(result_dict['startTimes'], predictions)

        plt.ylim([0, 1])
        
        path = 'src/devise/images/221116_1_CrexCrexAbsentPlots/' + file[:-4]
        plt.savefig(path, bbox_inches='tight')

        plt.clf()

#process_more_crex_crex_birdid_results()

print('Done.')