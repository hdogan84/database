from typing import List, Dict
from pathlib import Path
import derivates
from tools.logging import debug
from tools.configuration import DatabaseConfig, parse_config
from tools.db import (
    connectToDB,
)
from derivates import Standart22khz
from tools.multilabel import SimpleMultiLabels
import csv
import pandas as pd
import click
import numpy as np
import numpy.random as random
import matplotlib.pyplot as plt

CONFIG_FILE_PATH = Path("database/import_scripts/defaultConfig.cfg")

config = parse_config(CONFIG_FILE_PATH)


def compute_histogram_bins(data, desired_bin_size):
    min_val = np.min(data)
    max_val = np.max(data)
    min_boundary = -1.0 * (min_val % desired_bin_size - min_val)
    max_boundary = max_val - max_val % desired_bin_size + desired_bin_size
    n_bins = int((max_boundary - min_boundary) / desired_bin_size) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    return bins


def createDurationHistorgram(df):
    durations = df["duration"].to_numpy()
    val04 = len([number for number in durations if number < 0.5])
    val05 = len([number for number in durations if number >= 0.5 and number < 1])
    val10 = len([number for number in durations if number >= 1])
    print(val04)
    print(val05)
    print(val10)
    bins = compute_histogram_bins(durations, 0.1)
    plt.figure("Duration Historgram")
    plt.hist(durations, bins=bins)
    plt.xlabel("Duration in s")
    plt.ylabel("Counts")
    plt.title("Duration of labeled segement")
    plt.grid(True)


def createLabelLengthHistogramm(df):
    count = df["species_count"].to_numpy()
    bins = compute_histogram_bins(count, 1)
    plt.figure("Species count Histogram")
    plt.hist(count, bins=bins)
    plt.xlabel("count of labeld species ins segement")
    plt.ylabel("Counts")
    plt.title("Count of Species")
    plt.grid(True)


# @click.command()
# @click.argument("file_path", type=click.Path(exists=True))
def analyse_data(file_path):
    df = pd.read_csv(file_path, sep=";")
    createDurationHistorgram(df)
    createLabelLengthHistogramm(df)
    plt.show()


if __name__ == "__main__":
    # analyse_data("ammod-train-single-label.csv")
    analyse_data("ammod-train-multi-label.csv")
