import json
from logging import getLogger

from sqlalchemy import Engine, create_engine, text

from ..utils import load_config

logger = getLogger("oracle.app")

logger.info("Initializing Database...")

DB_CONFIG = load_config("DB_CONFIG")
DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
BASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}"

base_engine: Engine = create_engine(BASE_URL)

with base_engine.connect() as conn:
    result = conn.execute(
        text(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`;")
    )
    logger.info("Ensured Database Exists...")
    base_engine.dispose()

engine: Engine = create_engine(DATABASE_URL)


from .models import Base, IndicatorModel, OrderModel, PluginModel, ProfileModel
from .dtos import IndicatorDTO, OrderDTO, PluginDTO, ProfileDTO
from .operations import (create_indicator, create_order, create_plugin, create_profile,
                         delete_indicator, delete_plugin, delete_profile,
                         get_indicator, get_order, get_plugin, get_profile,
                         update_indicator, update_plugin, update_profile)

Base.metadata.create_all(engine)

logger.info("Database Successfully Initialized!")
