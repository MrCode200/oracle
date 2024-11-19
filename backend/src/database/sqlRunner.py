from logging import getLogger

from utils import load_query, prepare_connection

logger = getLogger("oracle.app")


@prepare_connection
def run_query(cursor, query_name: str = None, **kwargs) -> str:
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

    - **reset**

      **Purpose**: Deletes all data from all tables in the database named oracle.

    :param cursor: This argument should not be passed as it will be injected by the decorator.
    :param query_name: The name of the query to run, shouldn't be a path.
    :param kwargs: The parameters to pass to the query.
    :return: The results of the query.
    """
    logger.debug(f"Executing Query: {query_name}, with args: {kwargs}")
    cursor.execute(load_query(query_name), kwargs)
    return cursor.fetchall()
