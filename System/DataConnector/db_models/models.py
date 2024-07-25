from sqlalchemy import DateTime, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
from interfaces import UserRole, SubscriptionType, SubscriptionStatus

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    userID = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    password = Column(String(64), nullable=False)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    lastLogin = Column(DateTime, nullable=True)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscriptionID = Column(Integer, primary_key=True, autoincrement=True)
    userID = Column(Integer, ForeignKey('users.userID'), nullable=False)
    availableApiID = Column(Integer, ForeignKey('availableApi.availableApiID'), nullable=False)
    interval = Column(Integer, nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)


class AvailableApi(Base):
    __tablename__ = 'availableApi'

    availableApiID = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(200), nullable=False)
    description = Column(String(200), nullable=False)
    subscriptionType = Column(Enum(SubscriptionType), nullable=False)

