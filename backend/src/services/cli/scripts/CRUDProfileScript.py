from backend.src.database import delete_profile, get_profile, create_profile, create_indicator, ProfileDTO
from backend.src.services.indicators import SimpleMovingAverage
from backend.src.utils.registry import command_registry
from backend.src.services.entities.profile import Profile


@command_registry.register_function("add profile")
def command_add_profile():
    name = input("Enter the name :")
    wallet = input("Enter the wallet :")
    settings = input("Enter the settings :")

    new_profile_dot: ProfileDTO = create_profile(name, {"USD": int(wallet)}, {"buy_limit": settings, "sell_limit": 10})
    new_profile: Profile = Profile(new_profile_dot)
    new_indicator = SimpleMovingAverage()
    new_profile.add_indicator(
        indicator=new_indicator,
        weight=1,
        ticker="BTC",
        interval="1d"
    )

    print(new_profile_dot.id)


@command_registry.register_function("update profiles")
def command_update_profile():
    ...


@command_registry.register_function("display profile")
def command_display_profile():
    profiles = get_profile(0)
    print(profiles)


@command_registry.register_function(["del profile", "delete profile"])
def command_delete_profile():
    profile_name = input("Enter profile name: ")
    check = input(f"Are you sure you want to delete {profile_name}? (y/n): ")
    if check.lower() != "y":
        return
    print("Deleting profile...")
    delete_profile(profile_name=profile_name)
