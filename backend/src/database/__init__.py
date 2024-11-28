from logging import getLogger

from sqlalchemy import create_engine, text, Engine
import json


logger = getLogger("oracle.app")

logger.info("Initializing Database...")

with open('backend/config/config.json', 'r') as f:
    DB_CONFIG = json.load(f).get('DB_CONFIG')
DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
BASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}"

base_engine: Engine = create_engine(BASE_URL)

with base_engine.connect() as conn:
    result = conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`;"))
    logger.info("Ensured Database Exists...")
    base_engine.dispose()

engine: Engine = create_engine(DATABASE_URL)


from .models import Base, Profile, Order, Plugin, Indicator
from .operations import (get_profile, get_order, get_plugin, get_indicator,
                         create_profile, create_order, create_plugin, create_indicator,
                         delete_plugin, delete_profile, delete_indicator,
                         update_profile, update_plugin, update_indicator)


Base.metadata.create_all(engine)

logger.info("Database Successfully Initialized!")

