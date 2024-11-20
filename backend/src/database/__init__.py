from logging import getLogger

from sqlalchemy import create_engine, MetaData, Engine
import json


logger = getLogger("oracle.app")

logger.info("Initializing Database...")

with open('backend/config/config.json', 'r') as f:
    DB_CONFIG = json.load(f).get('DB_CONFIG')
DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

engine: Engine = create_engine(DATABASE_URL)


from .models import Base, Profile, Order
from .operations import (profileOperations, orderOperations,
                         select_profile, delete_profile, add_profile, insert_order, select_orders)


Base.metadata.create_all(engine)

logger.info("Database Successfully Initialized!")

