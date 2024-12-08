from logging import getLogger

from src.utils.registry import command_registry

logger = getLogger("oracle.app")


def init_cli():
    logger.info("Initializing Interface...")

    import src.services.cli.commands
    num_of_commands: int = len(command_registry.get())
    if num_of_commands == 0:
        raise Exception("No Commands Registered...")
    logger.info("All Commands Registered Successfully...")

    logger.info("Interface Initialized Successfully")

    print("Type `help` for a list of available commands.\n"
          "Type `exit` to exit the interface.")
    command = input("Enter a command: /")
    map_command(command)

    while command != "exit":
        command = input("Enter a command: /")
        map_command(command)


def map_command(command: str) -> None:
    command = command_registry.get(command.lower())
    if command is None:
        print("Command not found. Try /help for a list of available commands.")
        return
    elif command != "exit":
        command()