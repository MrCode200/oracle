from backend.src.api import fetch_info_data
from backend.src.exceptions import DataFetchError
from backend.src.algorithms.utils import get_model

def validate_profile(profile_name: str, balance: float, profile_settings: dict[str, any], wallet: dict[str, float],
                     algorithm_settings: dict[str, dict[str, any]], fetch_settings: dict) -> bool | ValueError:
    try:
        validate_profile_name(profile_name)
        validate_balance(balance)
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


def validate_balance(balance):
    if type(balance) is not float | int:
        raise ValueError("Balance must be a float.")
    if balance <= 0:
        raise ValueError("Balance must be greater than 0.")


def validate_profile_settings(profile_settings):
    if ["sell_threshold", "buy_threshold", "stop_loss", "limit"] not in profile_settings.keys():
        raise ValueError("Profile settings cannot contain sell_threshold, buy_threshold, stop_loss, or limit.")
    if profile_settings["sell_threshold"] < 0 or profile_settings["sell_threshold"] > -1:
        raise ValueError("Sell threshold must be between 0 and -1.")
    if profile_settings["buy_threshold"] < 0 or profile_settings["buy_threshold"] > 1:
        raise ValueError("Buy threshold must be between 0 and 1.")
    if profile_settings["stop_loss"] < 0 or profile_settings["stop_loss"] > 1:
        raise ValueError("Stop loss must be between 0 and 1.")
    if profile_settings["limit"] < 0 or profile_settings["limit"] > 1:
        raise ValueError("Limit must be between 0 and 1.")


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
    for model in algorithm_settings:
        if get_model(model) is None:
            raise ValueError(f"Invalid model: {model}")


def validate_fetch_settings(fetch_settings):
    if type(fetch_settings) is not dict:
        raise ValueError("Fetch settings must be a dictionary.")
    if ["period", "interval"] not in fetch_settings:
        raise ValueError("Fetch settings must contain period and interval.")