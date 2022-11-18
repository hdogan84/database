# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import pandas as pd
import soundfile as sf
import time

root_dir = "/mnt/z/Projekte/DeViSe/"


def process_csv_export_file():

    # Search for audacity label track txt files
    file_dir = "data/devise/WS_new/"
    input_csv_file = file_dir + "devise-WS_MfN_ARSU2021.csv"

    df = pd.read_csv(input_csv_file, header="infer", delimiter=";")
    print(df.columns)

    df = df.sort_values(["file_id", "start_time"])
    df = df.drop_duplicates()

    print(df)

    outpul_csv_file = file_dir + "devise-WS-MfN-ARSU2021.csv"
    df.to_csv(outpul_csv_file, index=False, sep=";")


# process_csv_export_file()


def negative_data_from_ammod_species():

    # Search for audacity label track txt files
    file_dir = "data/devise/WS_new/"
    input_csv_file = file_dir + "ammod-xc-tsa-shorts-val.csv"

    df = pd.read_csv(input_csv_file, header="infer", delimiter=";")
    df_new = pd.DataFrame(columns=df.columns)
    # print(df.iloc[0 + 1]["class_id"])

    for ix in range(0, len(df), 2):
        # Append rows of df
        if (
            df.iloc[ix + 1]["class_id"] != "Scolopax rusticola"
            and df.iloc[ix + 1]["class_id"] != "Crex crex"
        ):
            df_new = df_new.append(df.iloc[ix])
            df_new = df_new.append(df.iloc[ix + 1])

    # print(df)

    outpul_csv_file = file_dir + "ammod-xc-tsa-val-23species.csv"
    df_new.to_csv(outpul_csv_file, index=False, sep=";")


# negative_data_from_ammod_species()

def simplify_FVA_negatives():

    # Search for audacity label track txt files
    file_dir = "data/devise/WS_new/"
    input_csv_file = file_dir + "FVA-WS-absent.csv"

    df = pd.read_csv(input_csv_file, header="infer", delimiter=";")
    df_new = pd.DataFrame(columns=df.columns)

    for ix in range(0, len(df)):
        # Append rows of df
        if  df.iloc[ix]["class_id"] == "annotation_interval":
            df_new = df_new.append(df.iloc[ix])
            df_new = df_new.append(df.iloc[ix + 1])

    # print(df)

    outpul_csv_file = file_dir + "FVA-WS-absent-short.csv"
    df_new.to_csv(outpul_csv_file, index=False, sep=";")

simplify_FVA_negatives()

print("Done.")
