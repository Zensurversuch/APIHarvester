from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dbModels.models import AvailableApi

class AvailableApiRepository:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=self.engine)

    def getAvailableApis(self):
        try:
            session = scoped_session(self.session_factory)
            availableApis = session.query(AvailableApi).all()
            return availableApis
        except SQLAlchemyError as e:
            print(f"AvailableApiRepository: An error occurred while fetching all availableApis: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def getAvailableApisIds(self):
        try:
            session = self.session_factory()
            availableApisIds = session.query(AvailableApi.availableApiID).all()

            IdsArray = [id[0] for id in availableApisIds]
            return IdsArray
        except SQLAlchemyError as e:
            print(f"AvailableApiRepository: An error occurred while fetching all availableApis: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def getAvailableApiByID(self, paramAvailableApiID):
        try:
            session = scoped_session(self.session_factory)
            availableApi = session.query(AvailableApi).filter(AvailableApi.availableApiID == paramAvailableApiID).first()
            return availableApi
        except SQLAlchemyError as e:
            print(f"AvailableApiRepository: An error occurred while fetching availableApi with ID {paramAvailableApiID}: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def getAvailableApiBySubscriptionType(self, paramSubscriptionType):
        try:
            session = scoped_session(self.session_factory)
            subscriptions = session.query(AvailableApi).filter(AvailableApi.subscriptionType == paramSubscriptionType).all()
            return subscriptions
        except SQLAlchemyError as e:
            print(f"AvailableApiRepository: An error occurred while fetching availableApis with subscriptionType {paramSubscriptionType}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def createAvailableApi(self, paramUrl, paramName, paramDescription, paramSubscriptionType, paramRelevantFields):
        try:
            session = scoped_session(self.session_factory)
            newAvailableApi = AvailableApi( url = paramUrl,
                                            name = paramName, 
                                            description = paramDescription,
                                            subscriptionType = paramSubscriptionType,
                                            relevantFields = paramRelevantFields)	
            session.add(newAvailableApi)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"AvailableApiRepository: An error occurred while creating the availableApi: {e}")
            session.rollback()
            return False
        finally:
            session.close()
