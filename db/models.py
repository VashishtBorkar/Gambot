from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserEconomy(Base):
    __tablename__ = "economy"

    user_id = Column(Integer, primary_key=True)
    balance = Column(Integer, default=1000)