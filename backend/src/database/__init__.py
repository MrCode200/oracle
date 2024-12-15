from logging import getLogger

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL

from src.utils import load_config

logger = getLogger("oracle.app")

logger.info("Initializing Database...")

DB_CONFIG = load_config("DB_CONFIG")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["database"],
)
BASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
)

base_engine: Engine = create_engine(BASE_URL)

with base_engine.connect() as conn:
    result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'oracle'"))
    if result.fetchone() is None:
        conn.execute(text("CREATE DATABASE oracle"))
        logger.info("Database Successfully Created!")

engine: Engine = create_engine(DATABASE_URL)


from .dtos import IndicatorDTO, OrderDTO, PluginDTO, ProfileDTO
from .models import Base, IndicatorModel, OrderModel, PluginModel, ProfileModel
from .operations import (create_indicator, create_order, create_plugin,
                         create_profile, delete_indicator, delete_plugin,
                         delete_profile, get_indicator, get_order, get_plugin,
                         get_profile, update_indicator, update_plugin,
                         update_profile)

Base.metadata.create_all(engine)

logger.info("Database Successfully Initialized!")
