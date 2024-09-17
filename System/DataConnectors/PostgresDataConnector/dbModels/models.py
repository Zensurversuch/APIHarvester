from sqlalchemy import ARRAY, DateTime, Column, Integer, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import declarative_base
from commonRessources.interfaces import UserRole, SubscriptionType, SubscriptionStatus

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    userID = Column(Integer, primary_key=True, autoincrement=False)
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

    subscriptionID = Column(Integer, primary_key=True, autoincrement=False)
    userID = Column(Integer, ForeignKey('user.userID'), nullable=False)
    availableApiID = Column(Integer, ForeignKey('availableApi.availableApiID'), nullable=False)
    interval = Column(Integer, nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)
    jobName = Column(String(64), nullable=True)
    command = Column(String(512), nullable=True)
    container = Column(String(64), nullable=True)

    def toDict(self):
        return {
            'subscriptionID': self.subscriptionID,
            'userID': self.userID,
            'availableApiID': self.availableApiID,
            'interval': self.interval,
            'status': self.status.name,
            'jobName': self.jobName,
            'command': self.command,
            'container': self.container
        }

class AvailableApi(Base):
    __tablename__ = 'availableApi'

    availableApiID = Column(Integer, primary_key=True, autoincrement=False)
    url = Column(String(500), nullable=False)
    name = Column(String(200), nullable=False)
    apiTokenRequired = Column(Boolean, nullable=False)
    description = Column(String(200), nullable=False)
    subscriptionType = Column(Enum(SubscriptionType), nullable=False)
    relevantFields = Column(ARRAY(String), nullable=False)

    def toDict(self):
        return {
            'availableApiID': self.availableApiID,
            'url': self.url,
            'name': self.name,
            'apiTokenRequired': self.apiTokenRequired,
            'description': self.description,
            'subscriptionType': self.subscriptionType.name,
            'relevantFields': self.relevantFields
        }