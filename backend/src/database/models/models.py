from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Profile(Base):
    __tablename__ = "profiles"
    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_name = Column(String(50), unique=True)
    status = Column(Integer, default=0)
    profile_settings = Column(JSON)
    wallet = Column(JSON)
    algorithm_settings = Column(JSON)
    algorithm_weights = Column(JSON)
    fetch_settings = Column(JSON)


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("profiles.profile_id", ondelete="CASCADE"))
    type = Column(String(4))
    ticker = Column(String(16))
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=func.current_timestamp())