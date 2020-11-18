from typing import List, Dict
from pathlib import Path
from tools.configuration import DatabaseConfig
from tools.logging import debug
from tools.db import connectToDB, get_entry_id_or_create_it
from multiprocessing import cpu_count
from joblib import Parallel, delayed
import librosa


class Derivation:
    name: str
    id: int
    db_config: DatabaseConfig
    derivate_folder_path: Path

    def __init__(self, config: DatabaseConfig):
        self.db_config = config
        with connectToDB(config) as db_connection:
            with db_connection.cursor() as db_cursor:
                self.id = get_entry_id_or_create_it(
                    db_cursor,
                    "derivative",
                    [("name", self.name)],
                    [("name", self.name)],
                )
                self.derivate_folder_path = (
                    config.get_derivatives_files_path().joinpath(str(self.id))
                )

    def get_derivate(
        file_names: str, derivative_id: int, config: DatabaseConfig
    ) -> Path:
        """Return derivate filePath if exists or create Derivative"""
        raise NotImplementedError

    def add_derivate_to_dic(self, file_name: str, original_derivate_dict: dict) -> None:
        original_derivate_dict[file_name] = self.get_derivate(file_name)

    def get_original_derivate_dict(
        self, file_names: List[str], n_jobs=-1
    ) -> Dict[str, Path]:
        result_dict = {}

        use_n_jobs = n_jobs if n_jobs >= 0 else cpu_count()
        Parallel(n_jobs=use_n_jobs)(
            delayed(self.add_derivate_to_dic)(file_name, result_dict)
            for file_name in file_names
        )

        return result_dict


class Standart22khz(Derivation):
    name = "Standart22khz"

    def __init__(self, config: DatabaseConfig):
        super(Standart22khz, self).__init__(config)

    def get_derivate(
        self,
        file_name: str,
    ) -> Path:
        file_path: Path = self.db_config.get_originals_files_path().joinpath(file_name)
        target_file_path: Path = self.derivate_folder_path.joinpath(
            file_path.stem + ".wav"
        )
        debug("standart22khz {}".format(target_file_path.as_posix()))
        return target_file_path
