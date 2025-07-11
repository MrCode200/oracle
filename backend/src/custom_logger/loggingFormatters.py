import json
from logging import Formatter

# ANSI color codes for different log levels
LOG_COLORS: dict[str, str] = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "MSG": "\033[97m",  # Bright White
    "RESET": "\033[0m",  # Reset to default color
}
BOLD: str = "\033[1m"
UNDERLINE: str = "\033[4m"
RESET_UNDERLINE: str = "\033[24m"  # Resets underline only


class ColoredFormatter(Formatter):
    def format(self, record) -> str:
        log_color: str = LOG_COLORS.get(record.levelname, LOG_COLORS["RESET"])
        reset: str = LOG_COLORS["RESET"]
        white: str = LOG_COLORS["MSG"]

        # Assemble the final log message format
        formatted_message: str = (
            f"{log_color}{BOLD}[{UNDERLINE}{self.formatTime(record)}{RESET_UNDERLINE}] "
            f"{log_color}{BOLD}[{record.levelname} | {record.filename} | "
            f"lineno({record.lineno}) | {record.funcName}]{reset}\n"
        )

        # Append extra information if available, with labels underlined
        formatted_message += (
            f"{BOLD}"
            f"{UNDERLINE}tc:{RESET_UNDERLINE} {record.trading_component if 'trading_component' in record.__dict__ else 'None'}  |  "
            f"{UNDERLINE}Profile:{RESET_UNDERLINE} {record.profile_id if 'profile_id' in record.__dict__ else 'None'}\n"
        )

        # Append the main log message
        formatted_message += f"{white}Message: {record.getMessage()}{reset}"

        return formatted_message


class JsonFormatter(Formatter):
    def format(self, record) -> str:
        log_record: dict[str, any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "file": record.filename,
            "tc": record.trading_component if "trading_component" in record.__dict__ else None,
            "profile": record.profile_id if "profile_id" in record.__dict__ else None,
            "line_number": record.lineno,
            "function": record.funcName,
            "message": record.getMessage(),
            "exc_info": record.exc_info,
        }

        return json.dumps(log_record)
