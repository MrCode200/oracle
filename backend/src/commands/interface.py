from logging import getLogger

from backend.src.commands.utils import get_command

logger = getLogger("oracle.app")


def init_interface():
    logger.info("Initializing Interface...")

    import backend.src.commands.scripts
    num_of_commands: int = len(get_command())
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
    command = get_command(command.lower())
    if command is None:
        print("Command not found. Try /help for a list of available commands.")
        return
    command()
