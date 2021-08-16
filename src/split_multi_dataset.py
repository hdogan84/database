import csv
import random
from pathlib import Path
import argparse

# This script split a given csv in train and validation csv


def split_dataset(
    csv_filepath: Path, val_size=0.2, class_index=4, collection_id_index=3, file_id_index=1
):
    with open(csv_filepath) as dataFile:
        csv_data = csv.reader(dataFile, delimiter=";", quotechar="|",)
        fieldnames = csv_data.__next__()

        values = [i for i in csv_data]

        dict_files = {i[file_id_index]: [] for i in values}

        for x in values:
            dict_files[x[file_id_index]].append(x)

        dictClassIds = {}
        for key in dict_files:
            label_dict = {}
            for x in dict_files[key]:
                if(x[class_index] != 'annotation_interval'):
                    label_dict[x[class_index]] = True
            label_list = [ key for key in label_dict]
            label_list.sort()
            label = ','.join(label_list)
            if label in dictClassIds:
                dictClassIds[label].append(dict_files[key])
            else:
                 dictClassIds[label] = [dict_files[key]]

        

        result_val = []
        result_train = []
        for key in dictClassIds:
            random.shuffle(dictClassIds[key])
            split_at = round(len(dictClassIds[key]) * val_size)
            result_val.extend(dictClassIds[key][:split_at])
            result_train.extend(dictClassIds[key][split_at:])
        print(len(result_train))
        print(len(result_val))

        train_set = []
        val_set = []
        for x in result_train:
            train_set.extend(x)

        for x in result_val:
            val_set.extend(x)
        print(len(train_set))
        print(len(val_set))
       

        with open("val_{}".format(csv_filepath.name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
            writer.writerow(fieldnames)
            writer.writerows(val_set)

        with open("train_{}".format(csv_filepath.name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
            writer.writerow(fieldnames)
            writer.writerows(train_set)


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--csv",
    metavar="path",
    type=Path,
    nargs="?",
    help="csv file to split",
    default="./data/exported/210812_AMMOD_25Classes/long_files_ammod-multi-train.csv",
)


parser.add_argument(
    "--split",
    metavar="split",
    type=float,
    nargs="?",
    help="split for validation set",
    default=0.15,
)
parser.add_argument(
    "--class-index",
    metavar="class_index",
    type=int,
    nargs="?",
    default=4,
    help="index of column of class values",
)

parser.add_argument(
    "--collection-index",
    metavar="collection_index", 
    type=int,
    nargs="?",
    default=5,
    help="index of column of class values",
)
args = parser.parse_args()
if __name__ == "__main__":
    split_dataset(args.csv, val_size=args.split, class_index=args.class_index, collection_id_index=args.collection_index)
