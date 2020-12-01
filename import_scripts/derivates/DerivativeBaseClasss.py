from typing import List, Dict
from pathlib import Path
from tools.configuration import DatabaseConfig
from tools.db import connectToDB, get_entry_id_or_create_it
from joblib import Parallel, delayed
from tools.logging import error
from os import mkdir


class DerivativeBaseClass:
    name: str
    id: int
    db_config: DatabaseConfig
    derivate_folder_path: Path
    file_ending: str = None
    name: str = None
    sample_rate: int = None
    bit_depth: int = None
    description: str = None

    def __init__(
        self,
        config: DatabaseConfig,
    ):
        for field in ["name", "sample_rate", "bit_depth", "file_ending", "description"]:
            if getattr(self, field) is None:
                raise ValueError(
                    "Missing Class field {} for DerivativeClass, Please add it to your subclass".format(
                        field
                    )
                )
        self.db_config = config
        with connectToDB(config) as db_connection:
            with db_connection.cursor() as db_cursor:
                data = [
                    ("name", self.name),
                    ("sample_rate", self.sample_rate),
                    ("bit_depth", self.bit_depth),
                    ("description", self.description),
                ]
                self.id = get_entry_id_or_create_it(db_cursor, "derivative", data, data)
                db_connection.commit()
                self.derivate_folder_path = (
                    config.get_derivatives_files_path().joinpath(str(self.id))
                )
                if self.derivate_folder_path.exists() is False:
                    mkdir(self.derivate_folder_path)

    def create_derivate(source_file_path: Path, target_file_path: Path) -> None:
        """Return derivate filePath if exists or create Derivative"""
        raise NotImplementedError

    def add_derivate_to_dict(self, filename: str) -> None:
        source_file_path: Path = self.db_config.get_originals_files_path().joinpath(
            filename
        )
        if source_file_path.exists() is False:
            error("File Not found: {}".format(source_file_path.as_posix()))
            return None
        target_file_path: Path = self.derivate_folder_path.joinpath(
            source_file_path.stem + "." + self.file_ending
        )
        if target_file_path.exists() is False:
            self.create_derivate(source_file_path, target_file_path)
        return (filename, target_file_path)

    def get_original_derivate_dict(
        self, filenames: List[str], n_jobs=-1
    ) -> Dict[str, Path]:

        resultList = Parallel(n_jobs=n_jobs)(
            delayed(self.add_derivate_to_dict)(filename) for filename in filenames
        )

        return dict(resultList)
