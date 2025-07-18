from .botCommands import (start_app_command, status_app_command,
                          stop_app_command)
from .profileCommands import (change_status_command,
                              delete_profile_command, list_profiles_command,
                              create_profile_command, update_profile_command, backtest_profile_command)

from .walletCommands import update_wallet_command, view_wallet_command, clear_wallet_command

from .tradingComponentCommands import add_trading_component_command, remove_trading_component_command, \
    list_profile_trading_component_command, list_trading_components_command, update_trading_component_command
from .pluginCommands import add_plugin_command, update_plugin_command, remove_plugin_command, \
    list_profile_plugins_command, list_plugins_command
