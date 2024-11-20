from logging import getLogger

logger = getLogger("oracle.app")



def init_interface():
    command = input("Enter a command: ")

    while command != "/exit":
        command = input("Enter a command: ")
        map_command(command)


def map_command(command: str) -> str:
    return