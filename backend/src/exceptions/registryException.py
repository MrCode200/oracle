class RegistryError(Exception):
    """
    Custom exception raised when there is an error in registering data.
    """
    def __init__(self, message: str):
        """
        Initializes the RegistryError with a message.

        :param message: The error message to be raised with the exception.
        """

        super().__init__(message)