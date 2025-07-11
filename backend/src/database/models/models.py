from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer,
                        String, func, ARRAY)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ProfileModel(Base):  # type: ignore
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    status = Column(Integer, default=0)

    balance = Column(Float)
    wallet = Column(JSONB)

    paper_balance = Column(Float)
    paper_wallet = Column(JSONB)

    buy_limit = Column(Float)
    sell_limit = Column(Float)


class TradingComponentModel(Base):
    __tablename__ = "trading_components"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))

    name = Column(String(100))
    weight = Column(Float)
    ticker = Column(String(16))
    interval = Column(String(16))
    settings = Column(JSONB)


class PluginModel(Base):
    __tablename__ = "plugins"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))

    name = Column(String(100))
    settings = Column(JSONB)


class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"))

    type = Column(String(4))
    ticker = Column(String(16))
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=func.current_timestamp())
