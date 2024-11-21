COMMAND_REGISTRY: dict[str, callable] = {}


def register_command(*command_names) -> None:
    def wrapper(func):
        for command_name in command_names:
            if command_name in COMMAND_REGISTRY:
                raise Exception(f"Command {command_name} already registered")
            COMMAND_REGISTRY[command_name] = func

    return wrapper


def get_command(command: str = None) -> callable:
    if command is None:
        return COMMAND_REGISTRY
    return COMMAND_REGISTRY[command] if command in COMMAND_REGISTRY else None
