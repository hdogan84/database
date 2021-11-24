def map_filename_to_derivative_filepath(
    data_row: tuple, filename_index: dict, derivates_dict
):
    result = list(data_row)  #
    try:
        tmp_path = derivates_dict[result[filename_index]]
        if tmp_path is None:
            result[filename_index] = None
        else:
            result[filename_index] = tmp_path.as_posix()

    except KeyError as e:
        print("map_filename_to_derivative_filepath KeyError:", e)
        result[filename_index] = None
    return result
