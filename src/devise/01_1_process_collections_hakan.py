# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import pandas as pd
import soundfile as sf
import librosa

root_dir = "/mnt/z/Projekte/DeViSe/"
metadata_dir = root_dir + "Annotationen/"
lars_dir = "/mnt/z/AG/TSA/Lars_Beck/"
ARSU_dir = "/mnt/z/Projekte/DeViSe/Annotationen/ARSU_temp/"


def create_postfix_str(start_time, end_time, style="ms", include_end_time=True):

    # _500To20000ms
    postfix_str = (
        "_" + str(int(1000 * start_time)) + "To" + str(int(1000 * end_time)) + "ms"
    )

    # S00000500E00002000ms
    postfix_str = (
        "_S"
        + str(int(1000 * start_time)).zfill(7)
        + "E"
        + str(int(1000 * end_time)).zfill(7)
        + "ms"
    )

    postfix_str = "_S" + str(int(1000 * start_time)).zfill(7) + "ms"

    # Olaf style Shhmmss.ssEhhmmss.ss

    return postfix_str


def read_audacity_label_file(path, ignore_freq_range=False):

    if not os.path.isfile(path):
        print("Error: File not found", path)

    # Read audacity label track txt file
    df = pd.read_csv(path, sep="\t", header=None)
    # print(df)

    # Add header
    # df.columns = ['start_time', 'end_time', 'label']

    # Check if frequency ranges are included (every 2nd row starts with \)
    # Example, e.g.:
    """
    1192.760530	1193.424606	sp=Scolopax rusticola; ct=gr; ql=4; bg=2
    \	-1.000000	510.638306
    1193.424606	1193.522416	sp=Scolopax rusticola; ct=sq; ql=4; bg=2
    \	5361.702148	5531.914551
    """

    # Check for NaN values
    if df.isnull().values.any():
        print("Error: NaN value", path)
        return None
    else:

        # Check if "\" is at 2nd row first col
        if len(df.index) > 1 and df.iat[1, 0] == "\\":
            has_freq_range = True
            print("freq range info included in label file")
        else:
            has_freq_range = False

        if has_freq_range:

            if ignore_freq_range:
                # Remove freq range rows starting with \ (all odd rows) if ignore_freq_range
                df = df.drop(df[df.iloc[:, 0] == "\\"].index).reset_index(drop=True)
                # Add header
                df.columns = ["start_time", "end_time", "label"]
            else:
                # Include freq range as new cols start_freq and end_freq

                # Get start & end freq
                df_freq = df[df.iloc[:, 0] == "\\"]
                start_freq_list = df_freq.iloc[:, 1].tolist()
                end_freq_list = df_freq.iloc[:, 2].tolist()
                # print(df_freq)

                # Remove freq range rows starting with \ (all odd rows)
                df = df.drop(df[df.iloc[:, 0] == "\\"].index).reset_index(drop=True)
                # Add header
                df.columns = ["start_time", "end_time", "label"]

                # Add cols
                df["start_freq"] = start_freq_list
                df["end_freq"] = end_freq_list

                # Reorder cols
                df = df[["start_time", "end_time", "start_freq", "end_freq", "label"]]
                # print(df)

        else:
            # Add header
            df.columns = ["start_time", "end_time", "label"]

        # print(df)
        return df


def process_audacity_label_data(df):

    """
    example of label: sp=Crex crex; ct=s; ql=2; id=1; bg=0; cm=Hallo

    Artname (sp): Crex crex
    Lauttyp (ct): vorerst 3: s=Gesang, c=Ruf, i=instrumental (Trommeln o.ä.)
    Qualität (ql): 1 bis 5; 1 – sehr gut; 2 – gut; 3 – brauchbar; 4 – sehr schlecht; 5 – gerade noch zu hören
    Sicherheit d. Identifikation (id): 1 – zu 100% sicher, 2 – sehr sicher, 3 – unsicher
    Hintergrund (bg): 0 – kein Hintergrund; 1 – im Hintergrund andere Art, aber deutlich leiser; 2 - im Hintergrund andere Art deutlich
    Freies Feld (cm): alle anderen Kommentare
    """

    assignment_operator = "="
    separator = ";"

    key_tags = ["sp", "ct", "ql", "id", "bg", "cm"]
    key_names = [
        "species",
        "call_type",
        "quality",
        "id_level",
        "has_background",
        "comment",
    ]

    # ToDo: Sanity checks
    # assignment_operator, separator correct
    # what key_tags are used
    # are number of key_tags always the same

    n_rows = len(df.index)

    label_df_dict = {}
    for key in key_tags:
        label_df_dict[key] = [None] * n_rows

    for ix, row in df.iterrows():
        label_str = row["label"]
        # print(ix, label_str)

        # Split into labels
        labels = label_str.split(separator)
        # print(labels)

        for label in labels:
            # Remove leading and trailing whitespaces
            label = label.strip()
            # print(label)
            key_value_pair = label.split(assignment_operator)
            # print(key_value_pair)
            key = key_value_pair[0]
            value = key_value_pair[1]
            # print(key, value)

            if key not in key_tags:
                print("Error: Undefined key", key, ix, label)
            else:
                # Dequote comment string: "comment" --> comment
                if (
                    key == "cm"
                    and value[0] == value[-1]
                    and value.startswith(("'", '"'))
                ):
                    value = value[1:-1]

                label_df_dict[key][ix] = value

    # print(label_df_dict)

    # Check if there are label without any/some data
    for key in key_tags:
        if label_df_dict[key].count(None) == len(label_df_dict[key]):
            print(key, "has no data at all")
        else:
            if label_df_dict[key].count(None) > 0:
                print(key, "has no data sometimes")

    label_df = pd.DataFrame.from_dict(label_df_dict)
    # Rename cols (e.g. sp --> species)
    label_df.columns = key_names
    # print(label_df)

    # Remove label col from original df
    df = df.drop(columns=["label"])

    # Merge original df with extracted label df
    assert len(df.index) == len(label_df.index)
    df_concatenated = pd.concat([df, label_df], axis="columns")
    # print(df_concatenated)
    return df_concatenated


path = lars_dir + "Unteres_Odertal_2021_06_10/Devise02_2021-06-10T22-38-32_Pos01.txt"
# path = metadata_dir + '_BackupML/Devise07_2022-05-09T20-40-27_Annotation.txt'
path = lars_dir + "Criewen_2022_05_15/Criewen02/CRIEWEN02_20220515_202400.txt"
# df = read_audacity_label_file(path)
# print(df)
# process_audacity_label_data(df)


def process_ARSU_2022():

    key_names = [
        "filename",
        "start_time",
        "end_time",
        "start_freq",
        "end_freq",
        "vocalization_type",
        "quality",
        "id_level",
        "species",
        "has_background",
        "comment",
        "record_date",
        "record_time",
    ]

    df_list = pd.DataFrame(columns=key_names)

    key_names_final = [
        "filename",
        "channel_ix",
        "start_time",
        "end_time",
        "start_frequency",
        "end_frequency",
        "vocalization_type",
        "quality",
        "id_level",
        "has_background",
        "comment",
        "species_latin_name",
        "annotator_name",
        "recordist_name",
        "location_name",
        "record_date",
        "record_time",
        "collection_name",
        "record_filepath",
    ]

    # Search for audacity label track txt files
    root_src_dir = ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2022/"

    for root, dirs, files in os.walk(root_src_dir):
        for file in files:
            # Only use txt file with corresponing wav file
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                df = read_audacity_label_file(path, ignore_freq_range=False)
                #print(path)
                df = process_audacity_label_data(df)
                df = df.rename(columns={"call_type": "vocalization_type"})
                df["filename"] = file[:-15]
                df["record_date"] = file[9:19]
                df["record_time"] = file[20:28]
                df_list = pd.concat([df_list, df], ignore_index=True)

    # some numerical entries are somehow in str format. There is prob. a better way of dealing with this somewhere
    # else in the code
    
    for ix in range(len(df_list)):
        df_list["start_time"][ix] = float(df_list["start_time"][ix])
        df_list["end_freq"][ix] = float(df_list["end_freq"][ix])
        if df_list["id_level"][ix] is not None:
            df_list["id_level"][ix] = int(df_list["id_level"][ix])
        df_list["quality"][ix] = int(df_list["quality"][ix])
        df_list["has_background"][ix] = int(df_list["has_background"][ix])

    df_list["start_freq"] = df_list["start_freq"].replace([-1], 0)
    df_list["vocalization_type"] = df_list["vocalization_type"].replace("gr", "grunt")
    df_list["vocalization_type"] = df_list["vocalization_type"].replace("sq","squeak")
    df_list["annotator_name"] = "Steinkamp, Tim"
    df_list["recordist_name"] = "Steinkamp, Tim"
    df_list["location_name"] = "Gellener Torfmöörte"
    df_list["collection_name"] = "devise"
    df_list = df_list.rename(
        columns={
            "species": "species_latin_name",
            "start_freq": "start_frequency",
            "end_freq": "end_frequency",
        }
    )
    #df_list = df_list.drop(columns=["quality", "has_background", "comment"])
    df_list = df_list.sort_values(["filename", "start_time"])
    df_list = df_list.reindex(columns=key_names_final)

    outpul_excel_file = ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2022_v1.xlsx"
    #df_list.to_excel(outpul_excel_file, index=False)


#process_ARSU_2022()


def process_ARSU_2021():

    key_names = [
        "filename",
        "start_time",
        "end_time",
        "start_freq",
        "end_freq",
        "species",
        "vocalization_type",
        "comment",
        "record_date",
        "record_time",
    ]

    df_list = pd.DataFrame(columns=key_names)

    key_names_final = [
        "filename",
        "channel_ix",
        "start_time",
        "end_time",
        "start_frequency",
        "end_frequency",
        "vocalization_type",
        "id_level",
        "species_latin_name",
        "annotator_name",
        "recordist_name",
        "location_name",
        "record_date",
        "record_time",
        "collection_name",
        "record_filepath",
    ]

    # Search for audacity label track txt files
    root_src_dir = ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2021/"

    for root, dirs, files in os.walk(root_src_dir):
        for file in files:
            # Only use txt file with corresponing wav file
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                df = read_audacity_label_file(path, ignore_freq_range=False)
                # print(df)

                df = df.rename(columns={"label": "vocalization_type"})
                df["filename"] = file[:-15]
                df["record_date"] = file[9:19]
                df["species"] = "Scolopax rusticola"
                df["record_time"] = file[20:28]
                df = df.reindex(columns=key_names)
                df_list = pd.concat([df_list, df], ignore_index=True)

    print(df_list)

    # some numerical entries are somehow in str format. There is prob. a better way of dealing with this somewhere
    # else in the code
    for ix in range(len(df_list)):
        df_list["start_time"][ix] = float(df_list["start_time"][ix])
        df_list["end_freq"][ix] = float(df_list["end_freq"][ix])

    df_list["vocalization_type"] = df_list["vocalization_type"].replace(["g"], "gr")
    df_list["vocalization_type"] = df_list["vocalization_type"].replace(["s"], "sq")
    df_list["start_freq"] = df_list["start_freq"].replace([-1], 0)
    df_list["annotator_name"] = "Steinkamp, Tim"
    df_list["recordist_name"] = "Steinkamp, Tim"
    df_list["location_name"] = "Gellener Torfmöörte"
    df_list["collection_name"] = "devise_test"

    df_list = df_list.rename(
        columns={
            "species": "species_latin_name",
            "start_freq": "start_frequency",
            "end_freq": "end_frequency",
        }
    )
    df_list = df_list.drop(columns=["comment"])
    df_list = df_list.reindex(columns=key_names_final)
    df_list = df_list.sort_values(["filename", "start_time"])
    outpul_excel_file = ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2021_v1.xlsx"
    df_list.to_excel(outpul_excel_file, index=False)


#process_ARSU_2021()

def process_ARSU_segments():

    # Collect annotations from excel files
    xlsx_files = [
        #"Scolopax_rusticola_Devise_ARSU_2022_v1.xlsx",
        "Scolopax_rusticola_Devise_ARSU_2022_v1.xlsx",
    ]

    df_list= []
    for file in xlsx_files:
        path = ARSU_dir + file

        if not os.path.isfile(path):
            print("Error: File not found", path)

        df = pd.read_excel(path, engine="openpyxl")
        #print(df)
        #return
        df_list.append(df)
        print('n_rows', len(df))
        
    df = pd.concat(df_list).reset_index(drop=True)

    # Get unique audio files
    files = list(df["filename"].unique())
    n_files = len(files)
    # print(files)
    print("n_files", n_files)    

    # Create merged table
    df_merged_list = []

    df_merged_list = {}
    df_merged_list['filename'] = []
    df_merged_list['start_time'] = []
    df_merged_list['end_time'] = []

    filename = df.filename.values[0]
    start_time = df.start_time.values[0]
    end_time = df.end_time.values[0]
    # print(filename, start_time, end_time)

    max_time_without_annotation = 5  # 4

    for ix, row in df.iterrows():

        if (
            row["filename"] != filename
            or row["start_time"] - end_time > max_time_without_annotation
        ):
            # Add current values to df_merged_list
            df_merged_list["filename"].append(filename)
            df_merged_list["start_time"].append(start_time)
            df_merged_list["end_time"].append(end_time)
            # Init new
            filename = row["filename"]
            start_time = row["start_time"]
            end_time = row["end_time"]
        else:
            end_time = row["end_time"]

    # Add last row
    df_merged_list["filename"].append(filename)
    df_merged_list["start_time"].append(start_time)
    df_merged_list["end_time"].append(end_time)

    df_merged = pd.DataFrame.from_dict(df_merged_list)
    # print(df_merged)

    # Rename files according to annotation interval
    for ix, row in df_merged.iterrows():
        filename_new = row["filename"] + create_postfix_str(
            row["start_time"], row["end_time"]
        )
        df_merged.at[ix, "filename_new"] = filename_new
    # print(df_merged)

    # Create df with annotation times relative to cuttet parts
    df_new = df.copy()
    #print(df_new)

    for ix, row in df.iterrows():
        filename = row["filename"]
        channel_ix = row["channel_ix"]
        start_time = row["start_time"]
        end_time = row["end_time"]
        # print(start_time.dtype)

        # Find corresponding row in df_merged
        # df_merged_row = df_merged[df_merged.filename == filename & df_merged.start_time <= start_time & df_merged.end_time >= end_time]
        # df_merged_row = df_merged[df_merged.filename == filename & int(df_merged.start_time) <= start_time]

        df_merged_row = df_merged.loc[
            (df_merged["filename"] == filename)
            & (df_merged["start_time"] <= start_time)
            & (df_merged["end_time"] >= end_time)
        ].reset_index(drop=True)

        assert len(df_merged_row.index) == 1

        filename_new = df_merged_row.at[0, "filename_new"]
        start_time_new = start_time - df_merged_row.at[0, "start_time"]
        end_time_new = end_time - df_merged_row.at[0, "start_time"]

        # print(filename, start_time, end_time, channel_ix,  filename_new, df_merged_row.at[0, 'start_time'], df_merged_row.at[0, 'end_time'], start_time_new, end_time_new)

        df_new.at[ix, "filename"] = filename_new
        df_new.at[ix, "start_time"] = start_time_new
        df_new.at[ix, "end_time"] = end_time_new

    #print(df_new[["filename", "channel_ix", "start_time", "end_time"]])
    outpul_excel_file = ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2022_v3.xlsx"
    df_new.to_excel(outpul_excel_file, index=False)

process_ARSU_segments()

def process_ARSU_audiofiles(id):

    write_audio_files = True  # True False

    audio_root_src_dir = (
        ARSU_dir + "Scolopax_rusticola_Devise_ARSU_2022/"
    )
    audio_root_dst_dir = ARSU_dir + "_Segments/"

    # Read excel file
    path = ARSU_dir + id + ".xlsx"

    if not os.path.isfile(path):
        print("Error: File not found", path)

    df = pd.read_excel(path, engine="openpyxl")
    #print(df)
    print("n_rows", len(df))

    filenames = df["filename"].unique()
    n_filenames = len(filenames)
    #print(filenames)
    print("n_filenames", n_filenames)

    df_new=df.copy()

    for filename in filenames:

        df_sub=df[df["filename"]==filename]
        print(df_sub[["filename","start_time","end_time"]])

        path = audio_root_src_dir + "/" + filename[:-11] + ".flac"

        start_time = min(df_sub["start_time"])
        end_time = max(df_sub["end_time"])
        channel_ix = 0 #df_sub["channel_ix"]
        #print(start_time,end_time)

        # convert ms to sec
        time_offset=float(filename[-9:-2])/1000.0
        #print(time_offset)

        start_time+=time_offset
        end_time+=time_offset
        end_time = int(end_time)+1 # ceil the end time

        #print(start_time,end_time)

        if os.path.isfile(path):
            # Get audio file infos
            with sf.SoundFile(path) as f:
                samplerate = f.samplerate
                n_channels = f.channels

            start_ix = int(start_time * samplerate)
            end_ix = int(end_time * samplerate)
            if end_ix > f.frames: end_ix=f.frames

            #print(start_ix,end_ix,f.frames)

            filename_new = filename+'_c'+str(channel_ix)
            path_new = audio_root_dst_dir + "/" + filename_new + ".wav"

            data, samplerate = sf.read(
                path, start=start_ix, stop=end_ix, always_2d=True
            )
            if write_audio_files:
                sf.write(path_new, data[:, channel_ix], samplerate)

            #data, _ = librosa.load(path,sr=f.samplerate)

            #print(filename+'  done')

        else:
            print("Missing", path)


    #excel_path = audio_root_dst_dir + "test01.xlsx"
    #df_new.to_excel(excel_path, index=False, engine="openpyxl")

#process_ARSU_audiofiles('Scolopax_rusticola_Devise_ARSU_2022_v3')


# Crex_crex_Unteres_Odertal_2017
def process_collection(id):

    write_audio_files = False  # True False

    audio_root_src_dir = (
        root_dir + "Crex_crex_annotated/Crex_crex_Unteres_Odertal_2017_annotated/"
    )
    audio_root_dst_dir = root_dir + "Annotationen/_Segments/"

    # Read excel file
    path = metadata_dir + id + ".xlsx"

    if not os.path.isfile(path):
        print("Error: File not found", path)

    df = pd.read_excel(path, engine="openpyxl")
    # print(df)
    print("n_rows", len(df))

    filenames = df["filename"].unique()
    n_filenames = len(filenames)
    # print(filenames)
    print("n_filenames", n_filenames)

    # df_new stuff
    df_new_dict = {}
    keys = [
        "filename",
        "class",
        "collection_id",
        "channel_ix",
        "start_time",
        "end_time",
        "sub_dir",
    ]
    for key in keys:
        df_new_dict[key] = []

    for ix, row in df.iterrows():

        # if ix > 10: break

        # print(ix, row['filename'])

        filename = row["filename"]
        start_time = row["start_time"]
        end_time = row["end_time"]
        channel_ix = row["channel_ix"]

        path = audio_root_src_dir + row["sub_dir"] + "/" + filename + ".wav"

        if os.path.isfile(path):
            # Get audio file infos
            with sf.SoundFile(path) as f:
                samplerate = f.samplerate
                n_channels = f.channels

            start_ix = int(start_time * samplerate)
            end_ix = int(end_time * samplerate)
            data, samplerate = sf.read(
                path, start=start_ix, stop=end_ix, always_2d=True
            )

            filename_new = (
                filename
                + "_"
                + str(int(1000 * start_time))
                + "To"
                + str(int(1000 * end_time))
                + "ms"
            )

            if row["class"] == "Crex crex":
                class_new = "Crex_crex"
            if row["class"] == "BG":
                class_new = "Crex_crex_BG"

            path_new = audio_root_dst_dir + class_new + "/" + filename_new + ".wav"

            if write_audio_files:
                sf.write(path_new, data[:, channel_ix], samplerate)

            df_new_dict["filename"].append(filename_new + ".wav")
            df_new_dict["class"].append(class_new)
            df_new_dict["collection_id"].append(row["collection_id"])
            df_new_dict["channel_ix"].append(None)
            df_new_dict["start_time"].append(None)
            df_new_dict["end_time"].append(None)
            df_new_dict["sub_dir"].append(None)

            print(filename, data.shape, path_new)

        else:
            print("Missing", path)

    df_new = pd.DataFrame.from_dict(df_new_dict)
    print(df_new)

    excel_path = audio_root_dst_dir + "test01.xlsx"
    df_new.to_excel(excel_path, index=False, engine="openpyxl")


# process_collection('Crex_crex_Unteres_Odertal_2017')

# fva_test()


def process_hakan_schoenow():

    # Collect annotations from excel files
    xlsx_files = [
        "Scolopax_rusticola_MfN_Schoenow_2007.xlsx",
        "Scolopax_rusticola_MfN_Schoenow_2008.xlsx",
        "Scolopax_rusticola_MfN_Schoenow_2009.xlsx",
        "Scolopax_rusticola_MfN_Peenemuende_2014.xlsx",
    ]

    df_list = []
    for file in xlsx_files:
        path = metadata_dir + file

        if not os.path.isfile(path):
            print("Error: File not found", path)

        df = pd.read_excel(path, engine="openpyxl")
        # print(df)
        # print('n_rows', len(df))
        df_list.append(df)

    # Concat and sort
    df = pd.concat(df_list).reset_index(drop=True)
    df = df.sort_values(["filename", "start_time"]).reset_index(drop=True)
    print(df)

    # Get unique audio files
    files = list(df["filename"].unique())
    n_files = len(files)
    # print(files)
    print("n_files", n_files)

    # Sanity checks (end_time - start_time = 5s)
    for ix, row in df.iterrows():
        if row["end_time"] - row["start_time"] != 5:
            print("Warning end_time-start_time != 5", ix)

    # Create merged table

    df_merged_list = []

    df_merged_list = {}
    df_merged_list["filename"] = []
    df_merged_list["start_time"] = []
    df_merged_list["end_time"] = []

    filename = df.filename.values[0]
    start_time = df.start_time.values[0]
    end_time = df.end_time.values[0]
    # print(filename, start_time, end_time)

    max_time_without_annotation = 2  # 4

    for ix, row in df.iterrows():

        if (
            row["filename"] != filename
            or row["start_time"] - end_time > max_time_without_annotation
        ):
            # Add current values to df_merged_list
            df_merged_list["filename"].append(filename)
            df_merged_list["start_time"].append(start_time)
            df_merged_list["end_time"].append(end_time)
            # Init new
            filename = row["filename"]
            start_time = row["start_time"]
            end_time = row["end_time"]
        else:
            end_time = row["end_time"]

    # Add last row
    df_merged_list["filename"].append(filename)
    df_merged_list["start_time"].append(start_time)
    df_merged_list["end_time"].append(end_time)

    df_merged = pd.DataFrame.from_dict(df_merged_list)
    # print(df_merged)

    # Rename files according to annotation interval
    for ix, row in df_merged.iterrows():
        filename_new = row["filename"] + create_postfix_str(
            row["start_time"], row["end_time"]
        )
        df_merged.at[ix, "filename_new"] = filename_new
    # print(df_merged)

    # Create df with annotation times relative to cuttet parts
    df_new = df.copy()
    print(df_new)
    for ix, row in df.iterrows():
        filename = row["filename"]
        channel_ix = row["channel_ix"]
        start_time = row["start_time"]
        end_time = row["end_time"]
        # print(start_time.dtype)

        # Find corresponding row in df_merged
        # df_merged_row = df_merged[df_merged.filename == filename & df_merged.start_time <= start_time & df_merged.end_time >= end_time]
        # df_merged_row = df_merged[df_merged.filename == filename & int(df_merged.start_time) <= start_time]

        df_merged_row = df_merged.loc[
            (df_merged["filename"] == filename)
            & (df_merged["start_time"] <= start_time)
            & (df_merged["end_time"] >= end_time)
        ].reset_index(drop=True)

        assert len(df_merged_row.index) == 1

        filename_new = df_merged_row.at[0, "filename_new"]
        start_time_new = start_time - df_merged_row.at[0, "start_time"]
        end_time_new = end_time - df_merged_row.at[0, "start_time"]

        # print(filename, start_time, end_time, channel_ix,  filename_new, df_merged_row.at[0, 'start_time'], df_merged_row.at[0, 'end_time'], start_time_new, end_time_new)

        df_new.at[ix, "filename"] = filename_new
        df_new.at[ix, "start_time"] = start_time_new
        df_new.at[ix, "end_time"] = end_time_new

    print(df_new[["filename", "channel_ix", "start_time", "end_time"]])


# process_hakan_schoenow()

print("Done.")

