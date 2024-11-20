from logging import getLogger

import mysql.connector

from .utils import load_query, prepare_connection

logger = getLogger("oracle.app")


@prepare_connection
def run_query(cursor: mysql.connector.cursor_cext.CMySQLCursor, query_name: str = None, arg_map: dict[str, any] = None) -> str:
    """
    Loads and Runs queries from sql directory

    Available queries are stored in the 'sql' directory.

    **Available Queries**:

    - **load_profile**

      **Purpose**: Retrieves profile information from all profiles or a specific profile by name.

      **Parameters**:
        - ``profile_name`` (str): The profile name of the profile to retrieve. (OPTIONAL)

    - **load_profile_trans**

      **Purpose**: Retrieves all transactions of a specified profile by name.

      **Parameters**:
        - ``profile_name`` (str): The profile name of the profile to retrieve.

    - **add_profile**

      **Purpose**: Adds a new profile to the database.

      **Parameters**:
        - ``profile_name`` (str): The name of the new profile to add.
        - ``balance`` (float): The initial available balance of the new profile.
        - ``stop_loss`` (float): The stop loss value of the new profile.
        - ``wallet`` (dict): The wallet data of the new profile.
        - ``algorithms`` (dict): The algorithm data of the new profile.

    - **add_transaction**

      **Purpose**: Adds a new transaction to the database.

      **Parameters**:
        - ``profile_id`` (str): The ID of the profile associated with the transaction.
        - ``type`` (str): The type of the transaction. (Buy/Sell)
        - ``ticker`` (str): The ticker symbol of the coin.
        - ``quantity`` (float): The quantity of the coin bought.
        - ``price`` (float): The price the coin at the current time.
        - ``timestamp`` (str): The timestamp of the transaction.

    - **setup_db**

      **Purpose**: Initializes the database named oracle.

    - **reset_db**

      **Purpose**: Deletes all data from all tables in the database named oracle.

    :param cursor: This argument should not be passed as it will be injected by the decorator.
    :param query_name: The name of the query to run, shouldn't be a path.
    :param arg_map: The parameters to map to the query.
    :return: The results of the query.
    """
    if type(cursor) is not mysql.connector.cursor_cext.CMySQLCursor:
        raise AttributeError(f"You can't assign a cursor to this function. The type is {type(cursor)}")
    logger.debug(f"Executing Query: {query_name}, with args: {arg_map}")
    cursor.execute(load_query(query_name), arg_map)
    return cursor.fetchall()
