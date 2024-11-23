from logging import getLogger

logger = getLogger("oracle.app")

_COMMAND_REGISTRY: dict[str, callable] = {}


def register_command(*command_names) -> None:
    def wrapper(func):
        for command_name in command_names:
            if command_name in _COMMAND_REGISTRY:
                logger.warning(f"Command {command_name} already registered")
            else:
                _COMMAND_REGISTRY[command_name] = func

    return wrapper


def get_command(command: str = None) -> callable:
    if command is None:
        return _COMMAND_REGISTRY
    return _COMMAND_REGISTRY[command] if command in _COMMAND_REGISTRY else None
