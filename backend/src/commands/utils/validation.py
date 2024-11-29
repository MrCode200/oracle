from backend.src.api import fetch_info_data
from backend.src.exceptions import DataFetchError
from backend.src.utils.registry import indicator_registry

def validate_profile(profile_name: str, profile_settings: dict[str, any], wallet: dict[str, float],
                     algorithm_settings: dict[str, dict[str, any]], fetch_settings: dict) -> bool | ValueError:
    try:
        validate_profile_name(profile_name)
        validate_profile_settings(profile_settings)
        validate_wallet(wallet)
        validate_algorithm_settings(algorithm_settings)
        validate_fetch_settings(fetch_settings)
        return True
    except ValueError as e:
        return e


def validate_profile_name(profile_name):
    if not profile_name:
        raise ValueError("Profile name cannot be empty.")
    if type(profile_name) is not str:
        raise ValueError("Profile name must be a string.")
    if len(profile_name) > 50:
        raise ValueError("Profile name cannot be longer than 50 characters.")


def validate_profile_settings(profile_settings):
    if {"sell_limit", "buy_limit", "stop_loss", "limit"} == profile_settings.keys():
        raise ValueError("Profile settings cannot contain sell_limit, buy_limit, stop_loss, or limit.")
    if profile_settings["sell_limit"] < 0 or profile_settings["sell_limit"] > -1:
        raise ValueError("Sell limit must be between 0 and -1.")
    if profile_settings["buy_limit"] < 0 or profile_settings["buy_limit"] > 1:
        raise ValueError("Buy limit must be between 0 and 1.")
    if profile_settings["stop_loss"] < 0 or profile_settings["stop_loss"] > 1:
        raise ValueError("Stop loss must be between 0 and 1.")
    if profile_settings["limit"] < 0 or profile_settings["limit"] > 1:
        raise ValueError("Limit must be between 0 and 1.")
    if type(profile_settings["balance"]) is not float | int:
        raise ValueError("Balance must be a float.")
    if profile_settings["balance"] <= 0:
        raise ValueError("Balance must be greater than 0.")


def validate_wallet(wallet):
    if type(wallet) is not dict:
        raise ValueError("Wallet must be a dictionary.")
    for key in wallet:
        try:
            fetch_info_data(key)
        except DataFetchError:
            raise ValueError(f"Invalid ticker: {key}")


def validate_algorithm_settings(algorithm_settings):
    if type(algorithm_settings) is not dict:
        raise ValueError("Algorithm settings must be a dictionary.")
    for key in algorithm_settings:
        if type(algorithm_settings[key]) is not dict:
            raise ValueError("Algorithm settings must be a dictionary.")
    for indicator in algorithm_settings:
        if indicator_registry.get(indicator) is None:
            raise ValueError(f"Invalid indicator: {indicator}")


def validate_fetch_settings(fetch_settings):
    if type(fetch_settings) is not dict:
        raise ValueError("Fetch settings must be a dictionary.")
    if {"period", "interval"} == fetch_settings.keys():
        raise ValueError("Fetch settings must contain period and interval.")