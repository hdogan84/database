def write_to_csv(data, filename, header):
    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(
            csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(header)
        csv_writer.writerows(data)