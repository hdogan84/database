from typedconfig import Config, key, section, group_key
from typedconfig.source import EnvironmentConfigSource, IniFileConfigSource
from pathlib import Path
import errno
import os


@section("database")
class DatabaseConfig(Config):
    host: str = key(cast=str)
    port: int = key(cast=int)
    name: str = key(cast=str)
    user: str = key(cast=str)
    password: str = key(cast=str)
    file_storage_path: Path = key(cast=Path)


@section("record_information")
class RecordConfig(Config):
    recordist: str = key(cast=str)
    annotator: str = key(cast=str)
    location: str = key(cast=str)
    equipment: str = key(cast=str)


@section("files")
class FilesConfig(Config):
    annoation_file_ending: str = key(cast=str)
    record_file_ending: str = key(cast=str)


class ScriptConfig(Config):
    database: DatabaseConfig = group_key(DatabaseConfig)
    record_information: RecordConfig = group_key(RecordConfig)
    files: FilesConfig = group_key(FilesConfig)


def __validate_database_config(config: DatabaseConfig) -> bool:
    if config.file_storage_path.exists() is False:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config.file_storage_path
        )
    if config.file_storage_path.is_dir() is False:
        raise NotADirectoryError(
            errno.ENOTDIR, os.strerror(errno.ENOTDIR), config.file_storage_path
        )


def parse_config(config_file_path: Path, enviroment_prefix: str = None) -> ScriptConfig:
    if config_file_path.exists() is False:
        raise FileNotFoundError(config_file_path)

    config = ScriptConfig()
    if enviroment_prefix is not None:
        config.add_source(EnvironmentConfigSource(prefix=enviroment_prefix))
    config.add_source(IniFileConfigSource(config_file_path))
    config.read()
    __validate_database_config(config.database)
    return config
