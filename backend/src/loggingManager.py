import logging
from logging.handlers import RotatingFileHandler
import json


class JsonFormatter(logging.Formatter):
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


def setup_logging(stream_handler_level: int, log_in_json: bool = True) -> None:
    logger = logging.getLogger("oracle.app")
    logger.setLevel(logging.DEBUG)  # Set logger level

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(stream_handler_level)
    stream_handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s')
    )

    rotating_file_handler = RotatingFileHandler('logs/app.log', maxBytes=3 * (1024 * 1024), backupCount=3)
    rotating_file_handler.setLevel(logging.DEBUG)

    rotating_file_handler.setFormatter(
        JsonFormatter() if log_in_json
        else logging.Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
    )

    logger.addHandler(stream_handler)
    logger.addHandler(rotating_file_handler)