from backend.src.commands.utils import register_command, get_command
from backend.src.algorithms.utils import get_model

@register_command("help")
def command_help():
    print("Available commands:")
    for command in get_command().keys():
        print(command)


@register_command("list algorithms")
def command_list_algorithms():
    print("Available algorithms:")
    for algorithm in get_model().keys():
        print(algorithm)