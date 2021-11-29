def take_time(elem):
    return elem["time"]


#   0           1           2           3              4            5           6
# record_id, annoation_id, latin_name, german_name, english_name,start_time,end_time
def count_overlapping(annotation_list):
    file_dict = {}
    for entry in annotation_list:
        file_id = entry[0]
        if file_id not in file_dict:
            file_dict[file_id] = []
        file_dict[file_id].append(
            {
                "event": "start",
                "time": entry[5],
                "id": entry[1],
                "latin_name": entry[2],
                "english_name": entry[3],
                "german_name": entry[4],
            }
        )
        file_dict[file_id].append(
            {
                "event": "2nd",
                "time": entry[5],
                "id": entry[1],
                "latin_name": entry[2],
                "english_name": entry[3],
                "german_name": entry[5],
            }
        )
    # sort all file annotations
    for key in file_dict:
        file_dict[key].sort(key=take_time)
