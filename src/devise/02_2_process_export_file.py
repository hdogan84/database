# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import pandas as pd
import soundfile as sf
import time
import numpy as np

root_dir = "/mnt/z/Projekte/DeViSe/"


def process_csv_export_file():

    # This function sort the annotations start_time, to avoid errors in data loader
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

def merge_multiple_csv_export_files():

    # 
    file_dir = "data/devise/WK_WS_new/"
    input_csv_files = [ "WS-ARSU2022-pos-neg.csv", "WK-test-pos-neg.csv"]
    output_csv_file = "WK-WS-test-pos-neg.csv"

    df = pd.read_csv(file_dir + input_csv_files[0], header="infer", delimiter=";")

    df_merged = pd.DataFrame(columns=df.columns)

    for file in input_csv_files:

        df = pd.read_csv(file_dir + file, header="infer", delimiter=";")
        df_merged = pd.concat([df_merged, df], ignore_index=True)

    df_merged = df_merged.sort_values(["file_id", "start_time"])
    df = df.drop_duplicates()

    df_merged.to_csv(file_dir + output_csv_file, index=False, sep=";")

# merge_multiple_csv_export_files()


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

# simplify_FVA_negatives()


def shorten_XC_export():

    # Search for audacity label track txt files
    file_dir = "data/devise/derivate6/"
    input_csv_file = file_dir + "devise-ammod25-XC(calltype).csv"
    max_annotation = 200

    df = pd.read_csv(input_csv_file, header="infer", delimiter=";")
    species, counts = np.unique(df["class_id"], return_counts=True)
    species = species.tolist()
    species.remove("annotation_interval")
    counts=counts[:25]

    mydict=dict(zip(species,0*counts))

    df_new = pd.DataFrame(columns=df.columns)
    df_new2 = df_new

    # correct if 'annotation_interval' is occuring consequtively
    for ix in range(0, len(df)-1):

        anno_id = df.iloc[ix]["class_id"]
        class_id = df.iloc[ix+1]["class_id"]

        if anno_id == 'annotation_interval' and class_id != 'annotation_interval': 
            df_new = df_new.append(df.iloc[ix])
            df_new = df_new.append(df.iloc[ix + 1])


    # shorten the annotations to a max number
    for ix in range(0, len(df_new)-2, 2):

        class_id = df_new.iloc[ix+1]["class_id"]

        if mydict[class_id] > max_annotation:
            continue
        else:
            # Append rows of df
            df_new2 = df_new2.append(df_new.iloc[ix])
            df_new2 = df_new2.append(df_new.iloc[ix + 1])
            mydict[class_id] += 1

    #print(df_new)

    outpul_csv_file = file_dir + "devise-ammod25-XC-short.csv"
    df_new2.to_csv(outpul_csv_file, index=False, sep=";")

shorten_XC_export()


def compare_Xls_Csv_Testfiles():

    # Search for audacity label track txt files
    src_dir = root_dir + "Annotationen/_MetadataTestSets/"
    output_dir = "data/devise/WS_test/"

    input_xls_file = src_dir + "ScolopaxRusticolaAnnotations_v26_5s_Scores.xlsx"
    df = pd.read_excel(input_xls_file, engine='openpyxl')

    input_csv_file = output_dir + "WS-ARSU2022-pos-neg.csv"
    df2 = pd.read_csv(input_csv_file, header="infer", delimiter=";")
 
    print(len(df["filename"].unique()))
    print(len(df2["file_id"].unique()))


#compare_Xls_Csv_Testfiles()

print("Done.")
