import inspect
from functools import wraps
from logging import getLogger

import mysql.connector

logger = getLogger("oracle.app")

# load config.json rollbackonerror
ROLLBACK_ON_ERROR = True


def load_query(query_name: str) -> str:
    """
    Load a SQL query from a file.

    :param query_name: The name of the SQL file (without the .sql extension) to be loaded.
    :return: The contents of the SQL file as a string.
    :raises FileNotFoundError: If the specified SQL file does not exist.
    :raises IOError: If there is an error reading the file.
    """
    with open(f'../sql/{query_name}.sql', 'r') as file:
        return file.read()


_conn: mysql.connector.MySQLConnection | None = None
def prepare_connection(func: callable) -> callable:
    """
    A decorator to establish and manage a MySQL connection for the decorated function.
    The connection is created once and reused for subsequent calls, and error handling
    is incorporated with automatic reconnection attempts for certain errors.

    The decorated function must accept a 'cursor' parameter, which will be passed a
    MySQL cursor to interact with the database. If a database error occurs, it will
    try to reconnect and reattempt the query, if possible a rollback is performed to
    revert any uncommitted changes.

    :param func: The function to decorate. It must accept a 'cursor' parameter, which is
                 a MySQL cursor that interacts with the database.
    :raises AttributeError: If the decorated function does not accept a 'cursor' parameter.
    :return: A wrapper function that sets up a connection, manages the database interaction,
             handles errors, performs a rollback on failure, and closes the connection after execution.
    """
    if not inspect.signature(func).parameters.get("cursor"):
        raise AttributeError("The function must take a 'conn' attribute.")

    @wraps(func)
    def wrapper(*args, **kwargs) -> any:
        cursor: mysql.connector.cursor.MySQLCursor | None = None
        try:
            global _conn

            if _conn is None:
                _conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="root",
                    database="oracle"
                )

            cursor = _conn.cursor()
            results: any = func(cursor, *args, **kwargs)
            _conn.commit()
            cursor.close()
            return results

        except (mysql.connector.errors.InterfaceError, mysql.connector.errors.OperationalError) as e:
            if isinstance(e, mysql.connector.errors.InterfaceError):
                logger.error(
                    f"Database connection error: {e}, tried to execute: {func.__name__} with args: {args} and kwargs: {kwargs}")
            else:
                logger.error(
                    f"Operational error: {e}, tried to execute: {func.__name__} with args: {args} and kwargs: {kwargs}")

            if not _conn.is_connected():
                try:
                    logger.error("Reconnecting to database...")
                    _conn.reconnect(attempts=3, delay=3)
                except mysql.connector.errors.InterfaceError as reconnect_error:
                    logger.error(f"Failed to reconnect: {reconnect_error}")

        except Exception as e:
            logger.error(
                f"Unexpected error: {e}, tried to execute: {func.__name__} with args: {args} and kwargs: {kwargs}")

        finally:
            global _conn
            if cursor is not None:
                cursor.close()
            if _conn is not None and _conn.is_connected():
                logger.error("Rolling back and Closing database connection...")
                _conn.rollback()
                _conn.close()

    return wrapper
