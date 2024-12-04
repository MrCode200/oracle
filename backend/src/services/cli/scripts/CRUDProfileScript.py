from backend.src.commands.utils import register_command
from backend.src.database import delete_profile


@register_command("add profile")
def command_add_profile():
    ...


@register_command("update profiles")
def command_update_profile():
    ...


@register_command("display profile")
def command_display_profile():
    ...

@register_command("del profile", "delete profile")
def command_delete_profile():
    profile_name = input("Enter profile name: ")
    check = input(f"Are you sure you want to delete {profile_name}? (y/n): ")
    if check.lower() != "y":
        return
    print("Deleting profile...")
    delete_profile(profile_name=profile_name)