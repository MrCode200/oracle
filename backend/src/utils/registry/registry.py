from typing import Hashable, Dict, Any, Union
from logging import Logger, getLogger

from backend.src.exceptions import MissingKeyError, DuplicateError


class Registry:
    def __init__(self, registry_name: str = "BaseRegistry", log: bool = False, logger: Logger = None,
                 raise_exception: bool = True):
        """
        A generic base registry for storing and managing objects by key.

        :param registry_name: The name of the registry.
        :param log: Whether to enable logging for registry actions.
        :param logger: The logger instance to use for logging.
        :param raise_exception: Whether to raise exceptions on errors.
        """
        self._REGISTRY: Dict[Hashable, Any] = {}

        self.registry_name: str = registry_name
        self.log: bool = log
        self.logger = getLogger("root") if logger is None else logger
        self.raise_exception: bool = raise_exception

    @property
    def registry(self) -> Dict[Hashable, Any]:
        """
        Access the underlying registry.

        :return: The dictionary containing all registered items.
        :rtype: Dict[Hashable, Any]
        """
        return self._REGISTRY

    def register(self, keys: Union[Hashable, list[Hashable]], value: Any) -> None:
        """
        Register one or more keys with a specified value.

        :param keys: A single key or a list of keys to register.
        :param value: The value to associate with the given key(s).
        :raises DuplicateError: If a key is already registered and exceptions are enabled.
        """
        if not isinstance(keys, list):
            keys = [keys]

        for key in keys:
            if key in self._REGISTRY:
                if self.log:
                    self.logger.warning(f"{self.registry_name}: {key} already registered.")
                if self.raise_exception:
                    raise DuplicateError(f"{self.registry_name}: {key} already registered.",
                                         registry_name=self.registry_name, duplicate_item=key)
                return

            self._REGISTRY[key] = value
            if self.log:
                self.logger.debug(f"{self.registry_name}: Registered {key} to registry")

    def get(self, key: Union[Hashable, None] = None) -> Union[Dict[Hashable, Any], Any, None]:
        """
        Retrieve an item from the registry.

        :param key: The key to retrieve. If `None`, returns the entire registry.
        :return: The value associated with the key, or the entire registry if `key` is `None`.
        :raises NotRegisteredError: If the key is not registered and exceptions are enabled.
        """
        if key is None:
            return self._REGISTRY

        if key not in self._REGISTRY:
            if self.log:
                self.logger.warning(f"{self.registry_name}: {key} not registered.")
            if self.raise_exception:
                raise MissingKeyError(f"{self.registry_name}: {key} not registered.",
                                      registry_name=self.registry_name, missing_key=key)
            return None

        return self._REGISTRY[key]

    def remove(self, key: Union[Hashable, None] = None, value: Any = None) -> None:
        """
        Remove an item from the registry by key or value.

        :param key: The key to remove. If `None`, removal is based on the value.
        :param value: The value to remove. If `None`, removal is based on the key.
        :raises ValueError: If both `key` and `value` are `None`.
        :raises NotRegisteredError: If the key or value is not found and exceptions are enabled.
        """
        if key is None and value is None:
            raise ValueError("Either key or value must be provided.")

        if value is None:
            if key not in self._REGISTRY:
                if self.log:
                    self.logger.warning(f"{self.registry_name}: {key} not registered.")
                if self.raise_exception:
                    raise MissingKeyError(f"{self.registry_name}: {key} not registered.",
                                          registry_name=self.registry_name, missing_key=key)
                return

            del self._REGISTRY[key]
            if self.log:
                self.logger.debug(f"{self.registry_name}: Removed {key} from registry")

        else:
            for k, v in list(self._REGISTRY.items()):
                if v == value:
                    del self._REGISTRY[k]
                    if self.log:
                        self.logger.debug(f"{self.registry_name}: Removed {k} from registry")
                    return

            if self.log:
                self.logger.warning(f"{self.registry_name}: {value} not registered.")
            if self.raise_exception:
                raise MissingKeyError(f"{self.registry_name}: {value} not registered.",
                                      registry_name=self.registry_name, missing_key=value)

    def update(self, key: Hashable, value: Any) -> None:
        """
        Update an item in the registry.

        :param key: The key to remove. If `None`, removal is based on the value.
        :param value: The value to remove. If `None`, removal is based on the key.
        """
        if key not in self._REGISTRY:
            if self.log:
                self.logger.warning(f"{self.registry_name}: {key} not registered.")
            if self.raise_exception:
                raise MissingKeyError(f"{self.registry_name}: {key} not registered.",
                                      registry_name=self.registry_name, missing_key=key)
            return

        self._REGISTRY[key] = value
        if self.log:
            self.logger.debug(f"{self.registry_name}: Updated {key} in registry")

    def reset(self) -> None:
        """
        Clear all items from the registry.

        :return: None
        """
        self._REGISTRY.clear()
        if self.log:
            self.logger.debug(f"{self.registry_name}: Reset registry")
