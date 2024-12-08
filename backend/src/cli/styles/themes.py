from prompt_toolkit.styles import Style

dark_theme_style = Style.from_dict({
        "dialog": "bg:#1e1e1e #ffffff",         # Dark background, white text
        "dialog frame.label": "bg:#444444 #ffffff",  # Frame label style
        "button": "bg:#2d2d2d #ffffff",         # Buttons dark background
        "button.focused": "bg:#666666 #ffffff", # Focused button styling
    })