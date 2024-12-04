import logging
from logging import DEBUG, Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

from backend.src.custom_logger.loggingFormatters import (  # type: ignore
    ColoredFormatter, JsonFormatter)


def setup_logger(
    logger_name: str,
    stream_level: int,
    log_file_name: str,
    stream_in_color: bool = True,
    log_in_json: bool = True,
):
    custom_logger: logging.Logger = getLogger(logger_name)
    custom_logger.setLevel(DEBUG)

    stream_handler: logging.Handler = StreamHandler()
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(
        ColoredFormatter()
        if stream_in_color
        else Formatter(
            "[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s"
        )
    )

    timed_rotating_file_handler: logging.Handler = TimedRotatingFileHandler(
        log_file_name, when="midnight", interval=1, backupCount=3
    )
    timed_rotating_file_handler.setLevel(DEBUG)
    timed_rotating_file_handler.setFormatter(
        JsonFormatter()
        if log_in_json
        else Formatter(
            "[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s"
        )
    )

    custom_logger.addHandler(stream_handler)
    custom_logger.addHandler(timed_rotating_file_handler)

    custom_logger.propagate = False


if __name__ == "__main__":
    setup_logger(
        "oracle.app",
        DEBUG,
        "../../../logs/app.jsonl",
        log_in_json=False,
        stream_in_color=True,
    )

    logger = getLogger("oracle.app")
    logger.debug("Testing Logger: DEBUG")
    logger.info("Testing Logger: INFO")
    logger.warning("Testing Logger: WARNING")
    logger.error("Testing Logger: ERROR")
    logger.critical("Testing Logger: CRITICAL")
