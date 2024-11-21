from backend.src.commands.utils import register_command, get_command, validate_profile
from backend.src.database import add_profile, delete_profile
from backend.src.algorithms.utils import get_model

@register_command("add profile")
def command_add_profile():
    ...


@register_command("edit profiles")
def command_edit_profile():
    ...


@register_command("del profile", "delete profile")
def command_delete_profile():
    profile_name = input("Enter profile name: ")
    check = input(f"Are you sure you want to delete {profile_name}? (y/n): ")
    if check.lower() != "y":
        return
    print("Deleting profile...")
    delete_profile(profile_name=profile_name)
