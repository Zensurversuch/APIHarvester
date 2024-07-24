from sqlalchemy import DateTime, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
from interfaces import UserRole, SubscriptionType

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    userID = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    password = Column(String(64), nullable=False)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    lastLoggin = Column(DateTime, nullable=True)


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    subscriptionsID = Column(Integer, primary_key=True, autoincrement=True)
    userID = Column(Integer, ForeignKey('users.userID'), nullable=False)
    apiType = Column(String(50), nullable=False)
    interval = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)


class AvailableApis(Base):
    __tablename__ = 'availableApis'
    
    availableApisID = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(200), nullable=False)
    subscriptionType = Column(Enum(SubscriptionType), nullable=False)

