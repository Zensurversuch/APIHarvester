from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db_models.models import Subscription
from interfaces import SubscriptionStatus

class SubscriptionRepository:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=self.engine)

    def getSubscriptions(self):
        try:
            session = scoped_session(self.session_factory)
            subscriptions = session.query(Subscription).all()
            return subscriptions
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while fetching all subscriptions: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    

    def getSubscriptionByID(self, paramSubscriptionID):
        try:
            session = scoped_session(self.session_factory)
            subscription = session.query(Subscription).filter(Subscription.subscriptionID == paramSubscriptionID).first()
            return subscription
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while fetching user with ID {paramSubscriptionID}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def createSubscription(self, paramUserID, paramavalableApiID, paramInterval, paramSubscriptionStatus):
        try:
            session = scoped_session(self.session_factory)
            newSubscription = Subscription( userID=paramUserID,
                                availableApiID=paramavalableApiID,
                                interval=paramInterval, 
                                status= paramSubscriptionStatus)	
            session.add(newSubscription)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while creating the subscription: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def setSubsriptionStatus(self, paramSubscriptionID, paramSubscriptionStatus):
        try:
            session = scoped_session(self.session_factory)
            subscription = session.query(Subscription).filter(Subscription.subscriptionID == paramSubscriptionID).first()
            if subscription:
                return user
            return None
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while fetching user with Email {paramEmail}: {e}")
            session.rollback()
            return None
        finally:
            session.close()