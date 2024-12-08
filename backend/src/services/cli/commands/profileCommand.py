from src.services.entities import Profile
from src.utils.registry import command_registry, profile_registry


@command_registry.register_function(["activate profile", "act profile"])
def activate_profile():
    print("For a lists of all profiles type `list profiles`, to exit type `back`")

    def ask_for_profile_name():
        profile_name = "back"
        while profile_name in ["list profiles", "back"]:
            profile_name = input("Enter profile name: ")
            if profile_name == "back":
                return
            elif profile_name == "list profiles":
                command_registry.get("list profiles")()

        return profile_name

    profile: Profile = profile_registry.get(ask_for_profile_name())
    if profile is not None:
        profile.activate()
        print("Profile Activated Successfully (Hopefully...)")


@command_registry.register_function(["deactivate profile", "deact profile"])
def deactivate_profile():
    print("For a lists of all profiles type `list profiles`, to exit type `back`")

    def ask_for_profile_name():
        profile_name = "back"
        while profile_name in ["list profiles", "back"]:
            profile_name = input("Enter profile name: ")
            if profile_name == "back":
                return
            elif profile_name == "list profiles":
                command_registry.get("list profiles")()

        return profile_name

    profile: Profile = profile_registry.get(ask_for_profile_name())
    if profile is not None:
        profile.deactivate()
        print("Profile Deactivated Successfully (Hopefully...)")
