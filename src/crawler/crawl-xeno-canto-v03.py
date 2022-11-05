# https://xeno-canto.org/explore/api
# https://xeno-canto.org/help/search
# https://xeno-canto.org/search

import os
import requests
from datetime import datetime
import shutil
from pathlib import Path
import csv
import time
import pandas as pd



download_root_dir = "/net/mfnstore-lin/export/tsa_transfer/AudioData/xeno-canto/"


# recording_keys = ['id', 'gen', 'sp', 'ssp', 'group', 'en', 'rec', 'cnt', 'loc', 'lat', 'lng', 'alt', 'type', 'sex', 'stage', 'method', 'url', 'file', 'file-name', 'sono', 'osci', 'lic', 'q', 'length', 'time', 'date', 'uploaded', 'also', 'rmk', 'bird-seen', 'animal-seen', 'playback-used', 'temp', 'regnr', 'auto', 'dvc', 'mic', 'smp']
# # Remove keys not needed
# recording_keys.remove('sono')
# recording_keys.remove('osci')


def get_metadata(query, api_call_sleep_time=1.0, cols_to_drop=['sono', 'osci']):

    # Query can be species name but doesn't need to be

    '''
    For a successful query, a HTTP 200 response code will be returned, with a payload in the following format:
    {
                    "numRecordings": "1",
                    "numSpecies": "1",
                    "page": 1,
                    "numPages": 1,
                    "recordings": [
                        ...,
                        Array of Recording objects (dicts),
                        ...
                    ]
                }
    '''

    base_url = 'https://www.xeno-canto.org/api/2/recordings?query='

    # Make init api call to get basic infos (numRecordings, numSpecies, numPages)
    r = requests.get(base_url + query)
    if api_call_sleep_time:
        time.sleep(api_call_sleep_time)
    if r.status_code is 200:
        result = r.json()
        numRecordings = result['numRecordings']
        numSpecies = result['numSpecies']
        numPages = result['numPages']
        print('query: {}, numRecordings: {}, numSpecies: {}, numPages: {}'.format(
            query, 
            numRecordings, 
            numSpecies, 
            numPages))
    else:
        result = None
        print('Warning request for query {} returns {}'.format(query, r.status_code))


    # Iterate over pages and collect metadata of recordings
    df_list = []
    df = None
    if result:

        for page_ix in range(numPages):
            n_results_per_page = 0
            if page_ix == 0:
                result_per_page = result
            else:
                r = requests.get(base_url + query + '&page=' + str(page_ix+1))
                if api_call_sleep_time:
                    time.sleep(api_call_sleep_time)
                if r.status_code is 200:
                    result_per_page = r.json()
                else:
                    result_per_page = None
                    print('Warning request for query {} page {} returns {}'.format(query, page_ix+1, r.status_code))

            if result_per_page:
                recordings = result_per_page["recordings"]
                n_results_per_page = len(recordings)

                df_per_page = pd.DataFrame.from_dict(recordings)
                #print(df)
                df_list.append(df_per_page)

            print('page_ix', page_ix, 'n_recordings', n_results_per_page)

        df = pd.concat(df_list).reset_index(drop=True)

        # Drop cols not needed
        df = df.drop(columns=cols_to_drop)
        
        #print(df)
        
        # Write to excel file
        #df.to_excel(download_root_dir + 'test01.xlsx', index=False, engine='openpyxl')

    return df

def filter_metadata(df):

    # e.g. upload date
    #df = df.loc[df['uploaded'] > '2020-01-15']
    df = df.loc[df['uploaded'] < '2020-01-01']
    #df = df.loc[(df['uploaded'] >= '2020-01-01') & (df['uploaded'] < '2022-01-01')]

    # Reset index
    df = df.reset_index(drop=True)
    #print(df)
    
    return df

def download_files(df, download_dir, use_original_filename=False, download_file_sleep_time=1.0):

    # Create download directory if not existing
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # Iterate over recordings
    for ix, row in df.iterrows():
        id = row['id']
        url = row['file']
        original_filename = row['file-name']
        
        if use_original_filename:
            path = download_dir + original_filename
        else:
            file_extension = os.path.splitext(original_filename)[1].lower()
            path = download_dir + 'XC' + str(id) + file_extension

        print('Download: ' + path)
        with requests.get(url, stream=True) as r:
            with open(path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        
        if download_file_sleep_time:
            time.sleep(download_file_sleep_time)


query = 'Scolopax rusticola'
#df = get_metadata(query)

# # Write to csv/excel file
path_without_ext = download_root_dir + 'test02'
# df.to_csv(path_without_ext + '.csv', index=False)
# df.to_excel(path_without_ext + '.xlsx', sheet_name='Table', index=False, engine='openpyxl')

# Load from csv
df = pd.read_excel(path_without_ext + '.xlsx', keep_default_na=False, engine="openpyxl")
print(df)

# Filter metadata (adjust filter in function!)
df = filter_metadata(df)

#df = df.sort_values(['uploaded']).reset_index(drop=True)
df = df.sort_values(['id']).reset_index(drop=True)
print(df[['id','uploaded']])

download_dir = download_root_dir + 'xeno-canto-2022-10-20-02/'
download_files(df, download_dir, use_original_filename=False, download_file_sleep_time=1.0)

