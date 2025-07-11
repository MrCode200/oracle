from typing import Hashable


class RegistryError(Exception):
    """
    Custom exception raised when there is an error in registering data.
    """

    def __init__(self, message: str, registry_name: str = "BaseRegistry"):
        """
        Initializes the RegistryError with a message.

        :param message: The error message to be raised with the exception.
        :param registry_name: The name of the registry where the duplicate item is registered (optional).
        """
        self.registry_name = registry_name
        super().__init__(message)


class DuplicateError(RegistryError):
    """
    Custom exception raised when there is an attempt to register a duplicate entry.
    Inherits from RegistryError and adds specific behavior for duplicate errors.
    """

    def __init__(
        self,
        message: str | None = None,
        registry_name: str = "BaseRegistry",
        duplicate_item: Hashable = "",
    ):
        """
        Initializes the DuplicateError with a message and optional information about the duplicate item.

        :param message: The error message to be raised with the exception (Optional).
        :param registry_name: The name of the registry where the duplicate item is registered (optional).
        :param duplicate_item: The name or identifier of the duplicate item (optional).
        """
        self.message: str = (
            f"{registry_name}: Duplicate item = {duplicate_item}"
            if message is None
            else message
        )
        self.duplicate_item = duplicate_item
        super().__init__(self.message, registry_name)

    def __str__(self):
        if self.duplicate_item:
            return f"{self.args[0]}: {self.duplicate_item} in {self.registry_name}"
        return super().__str__()


class MissingKeyError(RegistryError):
    """
    Custom exception raised when a requested entry is not found in the registry.
    Inherits from RegistryError and adds specific behavior for not registered errors.
    """

    def __init__(
        self,
        message: str | None = None,
        registry_name: str = "BaseRegistry",
        missing_key: Hashable = "",
    ):
        """
        Initializes the NotRegisteredError with a message and optional information about the not registered item.

        :param message: The error message to be raised with the exception (Optional).
        :param registry_name: The name of the registry where the duplicate item is registered (optional).
        :param missing_key: The name or identifier of the not registered item (optional).
        """
        self.message: str = (
            f"{registry_name}: Not registered item = {missing_key}"
            if message is None
            else message
        )
        self.not_registered_item = missing_key
        super().__init__(self.message, registry_name)

    def __str__(self):
        if self.not_registered_item:
            return f"{self.args[0]}: {self.not_registered_item} in {self.registry_name}"
        return super().__str__()
