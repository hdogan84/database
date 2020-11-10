from mysql.connector import connect, MySQLConnection
from tools.configuration import DatabaseConfig
from tools.logging import debug


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
    if isinstance(value, float):  # round float for fixpoint saving in database
        return str(round(value, 6))
    return value
