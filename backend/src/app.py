import logging
import json

import sys

sys.path.append("/workspaces/oracle/backend")

from backend.src.custom_logger import setup_logger  # type: ignore
from backend.src.services import init_service
from backend.src.api import fetch_historical_data  # type: ignore
from backend.src.commands.interface import init_interface


def init_app():
    with open('backend/config/config.json', 'r') as f:
        log_config = json.load(f).get('LOG_CONFIG')

    setup_logger('oracle.app', log_config.get('level'), log_config.get('path'), log_config.get('stream_in_color'),
                 log_config.get('log_in_json'))
    logger = logging.getLogger("oracle.app")
    logger.info("Initialized Oracle...")

    import algorithms.indicators as indicators
    logger.info("All Indicators Registered Successfully...")

    init_service()

    init_interface()


init_app()