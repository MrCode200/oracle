def validate_profile_name(profile_name):
    if not profile_name:
        raise ValueError("Profile name cannot be empty.")
    if type(profile_name) is not str:
        raise ValueError("Profile name must be a string.")
    if len(profile_name) > 50:
        raise ValueError("Profile name cannot be longer than 50 characters.")
