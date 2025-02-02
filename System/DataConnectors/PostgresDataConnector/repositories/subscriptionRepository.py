from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from commonRessources.randomIDs import getRandomID
from dbModels.models import Subscription

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
            print(f"SubscriptionRepository: An error occurred while fetching subscription with ID {paramSubscriptionID}: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def getSubscriptionsByStatus(self, paramSubscriptionStatus):
        try:
            session = scoped_session(self.session_factory)
            subscriptions = session.query(Subscription).filter(Subscription.status == paramSubscriptionStatus).all()
            return subscriptions
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while fetching subscriptions with status {paramSubscriptionStatus}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def getSubscriptionsByUserID(self, paramUserID):
        try:
            session = scoped_session(self.session_factory)
            subscriptions = session.query(Subscription).filter(Subscription.userID == paramUserID).all()
            return subscriptions
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while fetching subscriptions with userID {paramUserID}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def createSubscription(self, paramUserID, paramavalableApiID, paramInterval, paramSubscriptionStatus, paramJobName):
        try:
            session = scoped_session(self.session_factory)
            randomID = getRandomID()
            while session.query(Subscription).filter(Subscription.subscriptionID == randomID).first() is not None:
                randomID = getRandomID()
                
            newSubscription = Subscription( subscriptionID=randomID,
                                            userID=paramUserID,
                                            availableApiID=paramavalableApiID,
                                            interval=paramInterval, 
                                            status=paramSubscriptionStatus,
                                            jobName=paramJobName)
            session.add(newSubscription)
            session.commit()
            return True, newSubscription.subscriptionID
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while creating the subscription: {e}")
            session.rollback()
            return False, None
        finally:
            session.close()

    def setSubsriptionStatus(self, paramSubscriptionID, paramSubscriptionStatus, paramJobName, paramCommand, paramContainer):
        try:
            session = scoped_session(self.session_factory)
            subscription = session.query(Subscription).filter(Subscription.subscriptionID == paramSubscriptionID).first()
            if subscription is None:
                print(f"SubscriptionRepository: No subscription found with ID {paramSubscriptionID}")
                return False

            if paramCommand is not None:
                subscription.command = paramCommand

            subscription.jobName = paramJobName
            subscription.container = paramContainer
            subscription.status = paramSubscriptionStatus

            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"SubscriptionRepository: An error occurred while updating the subscriptionStatus for subscriptionID {paramSubscriptionID}: {e}")
            session.rollback()
            return False
        finally:
            session.close()