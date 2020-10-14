from typedconfig import Config, key, section, group_key
from typedconfig.source import EnvironmentConfigSource, IniFileConfigSource


@section("database")
class DatabaseConfig(Config):
    host: str = key(cast=str)
    port: int = key(cast=int)
    name: str = key(cast=str)
    user: str = key(cast=str)
    password: str = key(cast=str)
    file_storage_path: str = key(cast=str)


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


def parse_config(config_file_path: str, enviroment_prefix: str = None) -> ScriptConfig:
    config = ScriptConfig()
    if enviroment_prefix is not None:
        config.add_source(EnvironmentConfigSource(prefix=enviroment_prefix))
    config.add_source(IniFileConfigSource(config_file_path))
    config.read()
    return config
