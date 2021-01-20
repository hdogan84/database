import csv
import random
from pathlib import Path
import argparse

# This script split a given csv in train and validation csv


def split_dataset(csv_filepath: Path, val_size=0.2, class_index=3):
    with open(csv_filepath) as dataFile:
        csv_data = csv.reader(dataFile, delimiter=";", quotechar="|",)
        fieldnames = csv_data.__next__()

        values = [i for i in csv_data]

        dictClassIds = {i[class_index]: [] for i in values}

        for x in values:
            dictClassIds[x[class_index]].append(x)

        result_val = []
        result_train = []
        for key in dictClassIds:
            random.shuffle(dictClassIds[key])
            split_at = round(len(dictClassIds[key]) * val_size)
            result_val.extend(dictClassIds[key][:split_at])
            result_train.extend(dictClassIds[key][split_at:])

        with open("val_{}".format(csv_filepath.name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
            writer.writerow(fieldnames)
            writer.writerows(result_val)

        with open("train_{}".format(csv_filepath.name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
            writer.writerow(fieldnames)
            writer.writerows(result_train)


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--csv", metavar="path", type=Path, nargs="?", help="csv file to split",
)


parser.add_argument(
    "--split",
    metavar="split",
    type=float,
    nargs="?",
    help="split for validation set",
    default=0.2,
)
parser.add_argument(
    "--index",
    metavar="index",
    type=int,
    nargs="?",
    default=3,
    help="index of column of class values",
)
args = parser.parse_args()
if __name__ == "__main__":
    split_dataset(args.csv, val_size=args.split, class_index=args.index)
