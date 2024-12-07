from backend.src.database import get_profile
from backend.src.services.entities import Status
from backend.src.utils.registry import command_registry, indicator_registry


@command_registry.register_function("help")
def command_help():
    print("Available commands:")
    for command in command_registry.get().keys():
        print(command)


@command_registry.register_function("list algorithms")
def command_list_algorithms():
    print("Available algorithms:")
    for indicator in indicator_registry.get().keys():
        print(indicator)


@command_registry.register_function("list profiles")
def command_list_profiles():
    profiles = get_profile()
    if len(profiles) == 0:
        print("No profiles created. Create a new Profile with the 'add profile' command.")
        return
    print("Available profiles:")
    for profile in profiles:
        print(f"ID: {profile.id}; Name: {profile.name} | Status: {Status(profile.status)}")
@command_registry.register_function("open profile")
def command_open_profile():
    name = input("enter the name :")
