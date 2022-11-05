# (conda install -c anaconda xlrd) # not working
# conda install -c anaconda openpyxl

import os
import pandas as pd
import soundfile as sf
import time

root_dir = "/mnt/z/Projekte/DeViSe/"
metadata_dir = root_dir + "Annotationen/"



def process_csv_export_file():

    # Search for audacity label track txt files
    file_dir = "data/devise/WK_train/"
    input_csv_file = file_dir + "devise-WK-Criewen-TSA-with-absent.csv"

    df = pd.read_csv(input_csv_file, header="infer", delimiter=";")
    print(df.columns)

    df = df.sort_values(["file_id", "start_time"])
    df = df.drop_duplicates()

    print(df)

    outpul_csv_file = file_dir + "WK-Criewen-TSA-pos-neg.csv"
    df.to_csv(outpul_csv_file, index=False, sep=";")


process_csv_export_file()


print("Done.")

