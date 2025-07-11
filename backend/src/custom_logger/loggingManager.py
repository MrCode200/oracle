import logging
from logging import DEBUG, Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler

from src.custom_logger.loggingFormatters import (  # type: ignore
    ColoredFormatter, JsonFormatter)


def setup_logger(
        logger_name: str,
        stream_level: int,
        log_file_name: str,
        add_stream_handler: bool = True,
        add_file_handler: bool = True,
        stream_in_color: bool = True,
        log_in_json: bool = True,
):
    """


    :param logger_name: The name of the logger
    :param stream_level: The logging.level of the stream handler
    :param log_file_name: The name of the log file
    :param add_stream_handler: If True, a stream handler will be added
    :param add_file_handler: If True, a file handler will be added
    :param stream_in_color: If True, the stream handler will be in color
    :param log_in_json: If True, the file handler will add the logging information in jsonl format
    :return:
    """
    custom_logger: logging.Logger = getLogger(logger_name)
    custom_logger.setLevel(DEBUG)

    if add_stream_handler:
        stream_handler: logging.Handler = StreamHandler()
        stream_handler.setLevel(stream_level)
        stream_handler.setFormatter(
            ColoredFormatter()
            if stream_in_color
            else Formatter(
                "[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s"
            )
        )

        custom_logger.addHandler(stream_handler)

    if add_file_handler:
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
