import csv
import random
from pathlib import Path
import argparse

# This script split a given csv in train and validation csv


def handle_xeno_canto(
    csv_filepath: Path, segment_length=10, start_index=5, end_index=6, collection_id_index=3, class_index=4
):
    with open(csv_filepath) as dataFile:
        csv_data = csv.reader(dataFile, delimiter=";", quotechar="|",)
        # remove head line with column names
        fieldnames = csv_data.__next__()
        values = [i for i in csv_data]
        
        index = 0
        result = []
        while index < len(values):

            x = values[index]
            if (x[collection_id_index] is "1"):
                if(x[class_index] != "annotation_interval"):
                    raise Exception("line {}: {} should be 'annotation_interval'".format(index,x[class_index]))
                if(float(x[end_index]) > segment_length*2):
                    # print('{} too long {}'.format(index, x[end_index]))
                    # add start annotation_interval
                    file_start = x.copy()
                    file_start[end_index] = segment_length
                    result.append(file_start)
                    # add start annotation
                    file_start = values[index+1].copy()
                    file_start[end_index] = segment_length
                   
                    result.append(file_start)
                    # add end annotation_interval
                    file_end = x.copy()
                    file_end[start_index] = float(file_end[end_index]) - segment_length
                    result.append(file_end) 
                    # add end annotation
                    file_end = values[index+1].copy()
                    file_end[start_index] = float(file_end[end_index]) - segment_length
                    result.append(file_end)
                else:
                    # print('{} short {}'.format(index, x[end_index]))
                    result.append(x)  
                    result.append(values[index+1])  
                index += 2
            else: 
                # print('{} no xeno'.format(index))
                result.append(x)
                index +=1

        print('Old length {} new length {}'.format(len(values),len(result)))
        with open("tmp_{}".format(csv_filepath.name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
            writer.writerow(fieldnames)
            writer.writerows(result)


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--csv",
    metavar="path",
    type=Path,
    nargs="?",
    help="csv file to split",
    default="./data/exported/210812_AMMOD_25Classes/ammod-multi-train.csv",
)       
args = parser.parse_args()
if __name__ == "__main__":
    handle_xeno_canto(args.csv)
