from backend.src.database import delete_profile, get_profile, create_profile, create_indicator
from backend.src.utils.registry import command_registry


@command_registry.register_function("add profile")
def command_add_profile():
    name = input("Enter the name :")
    wallet = input("Enter the wallet :")
    settings = input("Enter the settings :")

    new_profile=create_profile(name,{"USD":int(wallet)},{"buy_limit":settings,"sell_limit":10})
    ind=create_indicator(new_profile.id, "SimpleMovingAverage", {"long_period":51, "short_period":14}, ticker="BTC")
    print(get_profile(profile_name=name).id)


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