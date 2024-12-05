from backend.src.database import delete_profile
from backend.src.utils.registry import command_registry


@command_registry.register_function("add profile")
def command_add_profile():
    ...


@command_registry.register_function("update profiles")
def command_update_profile():
    ...


@command_registry.register_function("display profile")
def command_display_profile():
    ...

@command_registry.register_function(["del profile", "delete profile"])
def command_delete_profile():
    profile_name = input("Enter profile name: ")
    check = input(f"Are you sure you want to delete {profile_name}? (y/n): ")
    if check.lower() != "y":
        return
    print("Deleting profile...")
    delete_profile(profile_name=profile_name)