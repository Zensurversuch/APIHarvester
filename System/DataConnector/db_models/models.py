from sqlalchemy import ARRAY, DateTime, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
from interfaces import UserRole, SubscriptionType, SubscriptionStatus

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    userID = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    password = Column(String(64), nullable=False)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    lastLogin = Column(DateTime, nullable=True)

    def toDict(self):
        return {
            'userID': self.userID,
            'email': self.email,
            'lastName': self.lastName,
            'firstName': self.firstName,
            'role': self.role.name,  
            'lastLogin': self.lastLogin.isoformat() if self.lastLogin else None
        }

class Subscription(Base):
    __tablename__ = 'subscription'

    subscriptionID = Column(Integer, primary_key=True, autoincrement=True)
    userID = Column(Integer, ForeignKey('user.userID'), nullable=False)
    availableApiID = Column(Integer, ForeignKey('availableApi.availableApiID'), nullable=False)
    interval = Column(Integer, nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)

    def toDict(self):
        return {
            'subscriptionID': self.subscriptionID,
            'userID': self.userID,
            'availableApiID': self.availableApiID,
            'interval': self.interval,
            'status': self.status.name 
        }

class AvailableApi(Base):
    __tablename__ = 'availableApi'

    availableApiID = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(200), nullable=False)
    description = Column(String(200), nullable=False)
    subscriptionType = Column(Enum(SubscriptionType), nullable=False)
    relevantFields = Column(ARRAY(String), nullable=True)

    def toDict(self):
        return {
            'availableApiID': self.availableApiID,
            'url': self.url,
            'description': self.description,
            'subscriptionType': self.subscriptionType.name,
            'relevantFields': self.relevantFields
        }


