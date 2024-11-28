from backend.src.commands.utils import register_command, get_command
from backend.src.utils.registry import indicator_registry
from backend.src.database import select_profile

@register_command("help")
def command_help():
    print("Available commands:")
    for command in get_command().keys():
        print(command)


@register_command("list algorithms")
def command_list_algorithms():
    print("Available algorithms:")
    for algorithm in indicator_registry.registry().keys():
        print(algorithm)


@register_command("list profiles")
def command_list_profiles():
    profiles = select_profile()
    if len(profiles) == 0:
        print("No profiles created. Create a new Profile with the 'add profile' command.")
        return
    print("Available profiles:")
    for profile in profiles:
        print(f"{profile.profile_id}: {profile.profile_name} | Status: {profile.status}")