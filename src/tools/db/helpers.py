from mysql.connector import connect, MySQLConnection
from tools.configuration import DatabaseConfig
from tools.logging import debug


def connectToDB(config: DatabaseConfig) -> MySQLConnection:
    print("connect to db " + config.host + ":" + str(config.port) + "/" + config.name)
    return connect(
        host=config.host,
        port=config.port,
        user=config.user,
        passwd=config.password,
        database=config.name,
        auth_plugin="mysql_native_password",
    )


def to_sql_save_value(value):
    # if isinstance(value, float):  # round float for fixpoint saving in database
    #     return str(round(value, 6))
    return value


def sanitize_altitude(value: str):
    if value is None:
        return None
    result = value.strip()
    if result.startswith("<"):
        result = result.split("<")[1]
    tmp = result.split("-")
    if len(tmp) > 1:
        result = tmp[0]
    if result == "?" or result == "NULL":
        return None
    try:
        return int(result)
    except:
        return None


def sanitize_name(value: str, max_length: int):
    if value is None:
        return None
    if len(value) <= max_length:
        return value
    else:
        return value[:max_length]
