from logging import Formatter
import json


# ANSI color codes for different log levels
LOG_COLORS = {
    'DEBUG': '\033[94m',      # Blue
    'INFO': '\033[92m',       # Green
    'WARNING': '\033[93m',    # Yellow
    'ERROR': '\033[91m',      # Red
    'CRITICAL': '\033[95m',   # Magenta
    'MSG': '\033[97m',  # Bright White
    'RESET': '\033[0m',       # Reset to default color
}
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET_UNDERLINE = '\033[24m'   # Resets underline only


class ColoredFormatter(Formatter):
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, LOG_COLORS['RESET'])
        reset = LOG_COLORS['RESET']
        white = LOG_COLORS['MSG']

        # Assemble the final log message format
        formatted_message = (
            f"{log_color}{BOLD}[{UNDERLINE}{self.formatTime(record)}{RESET_UNDERLINE}] "
            f"{log_color}{BOLD}[{record.levelname} | {record.filename} | "
            f"lineno({record.lineno}) | {record.funcName}]{reset}\n"
        )

        # Append extra information if available, with labels underlined
        formatted_message += (
            f"{BOLD}"
            f"{UNDERLINE}Strategy:{RESET_UNDERLINE} {record.strategy if 'strategy' in record.__dict__ else 'None'}\n"
        )

        # Append the main log message
        formatted_message += f"{white}Message: {record.getMessage()}{reset}"

        return formatted_message

class JsonFormatter(Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "file": record.filename,
            "line_number": record.lineno,
            "function": record.funcName,
            "message": record.getMessage(),
        }

        return json.dumps(log_record)
