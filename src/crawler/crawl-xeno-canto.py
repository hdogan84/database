import requests

from datetime import datetime
import shutil
from pathlib import Path
import csv

species_list = [
    "Fringilla coelebs",
    "Scolopax rusticola",
    "Crex crex",
    "Chloris chloris",
    "Coccothraustes coccothraustes",
    "Spinus spinus",
    "Anthus trivialis",
    "Erithacus rubecula",
    "Ficedula hypoleuca",
    "Muscicapa striata",
    "Phoenicurus phoenicurus",
    "Cyanistes caeruleus",
    "Lophophanes cristatus",
    "Parus major",
    "Periparus ater",
    "Poecile palustris",
    "Phylloscopus sibilatrix",
    "Phylloscopus trochilus",
    "Sitta europaea",
    "Sylvia atricapilla",
    "Troglodytes troglodytes",
    "Turdus merula",
    "Turdus philomelos",
    "Turdus viscivorus",
    "Dendrocopos major",
]

download_path = "./downloads"
collection = "xeno_canto-ammod"
result_file = "collection-data.csv"
result_filepath = download_path + "/" + collection + "/" + result_file

end_date = datetime.strptime("2020-05-01", "%Y-%m-%d")


def write_to_csv(data, filename, header) -> None:
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(
            csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        if header is not None:
            csv_writer.writerow(header)
        csv_writer.writerows(data)


def download_file(url, local_filename, subfolder=None):
    print("Start download " + url + " " + local_filename)
    download_folder = (
        download_path + "/" + collection + (subfolder if subfolder is not None else "")
    )
    Path(download_folder).mkdir(parents=True, exist_ok=True)
    print("Download file: " + local_filename)
    with requests.get(url, stream=True) as r:
        with open(download_folder + "/" + local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename


def duration_string_to_seconds(duration):
    tmp = duration.split(":")
    if len(tmp) is 2:
        return int(tmp[0]) * 60 + int(tmp[1])
    if len(tmp) is 3:
        return int(tmp[0]) * 60 * 60 + int(tmp[1]) * 60 + int(tmp[2])


def make_api_call(species, page=None):
    
    # parameter dir & order not used in api
    # r = requests.get(
    #     "https://www.xeno-canto.org/api/2/recordings?query={}&dir=1&order=dt".format(
    #         species
    #     )
    #     + ("&page={}".format(page) if page is not None else "")
    # )
    r = requests.get(
        "https://www.xeno-canto.org/api/2/recordings?query={}".format(
            species
        )
        + ("&page={}".format(page) if page is not None else "")
    )
    if r.status_code is 200:
        return r.json()
    else:
        print(
            "Warning reuest {}  on page {} returns {}".format(
                species, page, r.status_code
            )
        )
        return None


download_till_date = ""
csv_entries = []
for species in species_list:
    result = make_api_call(species)
    print(result["numRecordings"])
    print(
        "Found {} recordings for {} with num species".format(
            result["numRecordings"], species, result["numSpecies"]
        )
    )
    for page in range(1, result["numPages"]):
        print(page)
        result = make_api_call(species, page=page)
        break_page_iteration = False
        for index, record in enumerate(result["recordings"]):
            upload_date = datetime.strptime(record["uploaded"], "%Y-%m-%d")

            if upload_date < end_date:
                print("Reached end date on page {} record {}".format(page, index))
                break_page_iteration = True
                break
            filepath = download_file("https:" + record["file"], record["file-name"])
            record_csv_entry = [
                record["rec"].replace(";", ","),  # recordist sanitize ;
                record["loc"].replace(";", ","),  # location sanitize ;
                record["lat"],  # latitude
                record["lng"],  # longitude
                record["alt"],  # altitude
                record["file-name"],  # original_filename
                record["id"],  # xeno_canto_id
                record["type"].replace(";", ","),  # call_type
                record["date"],  # date
                record["time"],  # time
                duration_string_to_seconds(record["length"]),  # duration
            ]
            species_csv_entry = [species, False]  # species  # isBackground
            csv_entries.append(record_csv_entry + species_csv_entry)
            for background_species in record["also"]:
                if background_species == "":
                    continue
                species_csv_entry = [
                    background_species,  # species
                    True,  # isBackground
                ]
                csv_entries.append(record_csv_entry + species_csv_entry)

        if break_page_iteration:
            break
        #     print(record["uploaded"])
    headline = [
        "recordist",
        "location_name",
        "latitude",
        "longitude",
        "altitude",
        "original_filename",
        "xeno_canto_id",
        "call_type",
        "date",
        "time",
        "species",
        "background",
    ]
    write_to_csv(csv_entries, result_filepath, headline)
