from mysql.connector import connect, MySQLConnection
from tools.configuration import DatabaseConfig


def connectToDB(config: DatabaseConfig) -> MySQLConnection:
    return connect(
        host=config.host,
        port=config.port,
        user=config.user,
        passwd=config.password,
        database=config.name,
        auth_plugin="mysql_native_password",
    )


def to_sql_save_value(value):
    if value is None:
        return "null"
    if isinstance(value, int):
        return value
    if isinstance(value, float):  # round float for fixpoint saving in database
        return str(round(value, 6))
    if isinstance(value, str):
        return value
    return "{}".format(value)
