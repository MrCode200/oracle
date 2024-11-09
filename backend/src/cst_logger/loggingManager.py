import logging
from logging import getLogger

from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

from logging import DEBUG

from logging import Formatter
from .loggingFormatters import ColoredFormatter, JsonFormatter  # type: ignore


def setup_logger(stream_level: int, log_file_name: str, stream_in_color: bool = True, log_in_json: bool = True):
    logger: logging.Logger = getLogger('oracle.app')
    logger.setLevel(DEBUG)

    stream_handler: logging.Handler = StreamHandler()
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(
        ColoredFormatter() if stream_in_color else Formatter(
            '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
    )


    timed_rotating_file_handler: logging.Handler = TimedRotatingFileHandler(log_file_name, when='midnight', interval=1, backupCount=3)
    timed_rotating_file_handler.setLevel(DEBUG)
    timed_rotating_file_handler.setFormatter(
        JsonFormatter() if log_in_json else Formatter(
        '[%(asctime)s | %(levelname)s] [%(filename)s | lineno%(lineno)d | %(funcName)s] => %(message)s'
        )
    )

    logger.addHandler(stream_handler)
    logger.addHandler(timed_rotating_file_handler)

    logger.propagate = False


if __name__ == '__main__':
    setup_logger(DEBUG, '../../../logs/app.jsonl',log_in_json=False, stream_in_color=True)

    logger = getLogger('oracle.app')
    logger.debug('Testing Logger: DEBUG', extra={'command': 'test', 'author': 'wobble', 'guild': 'wobble#0000'})
    logger.info('Testing Logger: INFO', extra={'command': 'test', 'author': 'wobble'})
    logger.warning('Testing Logger: WARNING')
    logger.error('Testing Logger: ERROR')
    logger.critical('Testing Logger: CRITICAL')