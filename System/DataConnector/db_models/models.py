from sqlalchemy import create_engine, MetaData, Column, Integer, String, Date, Table, ForeignKey, ARRAY, LargeBinary, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __tablename__ = 'users'

    userID = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    password = Column(String(64), nullable=False)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)