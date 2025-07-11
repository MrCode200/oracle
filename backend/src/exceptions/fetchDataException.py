class DataFetchError(Exception):
    """
    Custom exception raised when there is an error fetching data.
    This can be used for different types of data fetching errors.
    """

    default_exception_message = "Error occurred while Fetching data."

    def __init__(self, message: str | None = None, **kwargs):
        """
        Initializes the DataFetchError with a default message and optional parameters.

        :param message: The error message to be raised with the exception. (optional)
        :key kwargs: Additional parameters to be passed to the exception message. They will be appended to the error message
        """
        message = (
            message if message is not None else DataFetchError.default_exception_message
        )

        message += "\nArguments passed: " + str(kwargs)

        super().__init__(message)
