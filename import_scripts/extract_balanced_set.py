import csv
import random

DATA_FILEPATH = (
    "/home/bewr/projects/mfn/audio_classificator/data/ammod-selection/labels.csv"
)
CLASS_FILEPATH = (
    "/home/bewr/projects/mfn/audio_classificator/data/ammod-selection/class-list.csv"
)
with open(CLASS_FILEPATH) as classFile, open(DATA_FILEPATH) as dataFile:
    dataframe = csv.reader(
        dataFile,
        delimiter=";",
        quotechar="|",
    )
    fieldnames = dataframe.__next__()
    classlist = csv.reader(
        classFile,
        delimiter=";",
        quotechar="|",
    )
    classlist.__next__()
    classIds = []
    for x in classlist:
        classIds.append(x[0])

    dictClassIds = {i: [] for i in classIds}

    for x in dataframe:
        dictClassIds[x[3]].append(x)
    print(dictClassIds)
# get min length of class
min_length = dataframe.line_num
for key in dictClassIds:
    if len(dictClassIds[key]) < min_length:
        print(key, "->", len(dictClassIds[key]))
        min_length = len(dictClassIds[key])

result = []
for key in dictClassIds:
    random.shuffle(dictClassIds[key])
    result.extend(dictClassIds[key][:min_length])

with open("balanced_datas.csv", "w", newline="") as csvfile:
    writer = csv.writer(
        csvfile,
        delimiter=";",
        quotechar="|",
    )
    writer.writerow(fieldnames)
    writer.writerows(result)