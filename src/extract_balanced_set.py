import csv
import random

INDEX_CLASS_ID = 4
# This script extract from an exported ammod csv a ballanced dataset,
# smallest amount samples of a class defines amount for all other classes
DATA_FILEPATH = "/home/tsa/projects/libro-animalis/data/exported/210812_AMMOD_25Classes/ammod-multi-val.csv"
CLASS_FILEPATH = "ammod-class-list.csv"
with open(CLASS_FILEPATH) as classFile, open(DATA_FILEPATH) as dataFile:
    dataframe = csv.reader(dataFile, delimiter=";", quotechar="|",)
    fieldnames = dataframe.__next__()
    classlist = csv.reader(classFile, delimiter=";", quotechar="|",)
    classlist.__next__()
    classIds = []
    for x in classlist:
        classIds.append(x[0])

    dictClassIds = {i: [] for i in classIds}

    for x in dataframe:
        if(x[INDEX_CLASS_ID] == 'annotation_interval'):
            continue
        dictClassIds[x[INDEX_CLASS_ID]].append(x)
    # print(dictClassIds)
# get min length of class
min_length = dataframe.line_num
for key in dictClassIds:
    if len(dictClassIds[key]) < min_length:
        print(key, "->", len(dictClassIds[key]))
        min_length = len(dictClassIds[key])
counter = 0
for key in dictClassIds:
    print('{} {}: {}'.format(counter, key,len(dictClassIds[key])))
    counter +=1
result = []
for key in dictClassIds:
    random.shuffle(dictClassIds[key])
    result.extend(dictClassIds[key][:min_length])

with open("balanced_labels.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=";", quotechar="|",)
    writer.writerow(fieldnames)
    writer.writerows(result)
