def load_query(query_name: str) -> str:
    """
    Load a SQL query from a file.

    Available queries are stored in the 'sql' directory.

    **Available Queries**:

    - **load_profile_by_name**

      **Purpose**: Retrieves profile information from specified columns and profile name.

      **Parameters**:
        - ``columns`` (str): A comma-separated list or * of columns to retrieve from the profile table.
        - ``profile_name`` (str): The profile name of the profile to retrieve.

    - **load_profile_trans**

      **Purpose**: Retrieves all transactions of a specified profile by name.

      **Parameters**:
        - ``columns`` (str): A comma-separated list or * of columns to retrieve from the profile table.
        - ``profile_name`` (str): The profile name of the profile to retrieve.

    - **load_profiles**

      **Purpose**: Loads specified columns of all profiles.

      **Parameters**:
        - ``columns`` (str): A comma-separated list or * of columns to retrieve from the profile table.


    - **setup_db**

      **Purpose**: Initializes the database named oracle.

    - **reset**

      **Purpose**: Deletes all data from all tables in the database named oracle.


    :param query_name: The name of the SQL file (without the .sql extension) to be loaded.
    :type query_name: str
    :return: The contents of the SQL file as a string.
    :rtype: str
    :raises FileNotFoundError: If the specified SQL file does not exist.
    :raises IOError: If there is an error reading the file.
    """
    with open(f'../sql/{query_name}.sql', 'r') as file:
        return file.read()