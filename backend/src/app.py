from logging import DEBUG, INFO
from custom_logger.loggingManager import setup_logger  # type: ignore


def init_app():
    setup_logger("oracle.app", DEBUG, "../../../logs/app.jsonl")


if __name__ == "__main__":
    init_app()
