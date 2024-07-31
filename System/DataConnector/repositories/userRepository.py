from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db_models.models import User
from random import randint 
import hashlib

class UserRepository:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=self.engine)

    def createUser(self, paramEmail, paramPassword, paramLastName, paramFirstName, paramRole):
        try:
            session = scoped_session(self.session_factory)
            hashedPassword = hashlib.sha256(paramPassword.encode('utf-8')).hexdigest()
            newUser = User( email=paramEmail,
                            password=hashedPassword,
                            lastName=paramLastName,
                            firstName=paramFirstName,
                            role=paramRole)
            session.add(newUser)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while creating the user: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    

    def getUsers(self):
        try:
            session = scoped_session(self.session_factory)
            users = session.query(User).all()
            return users
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while fetching all users: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def getUserByID(self, paramUserID):
        try:
            session = scoped_session(self.session_factory)
            user = session.query(User).filter(User.userID == paramUserID).first()
            if user:
                return user
            return None
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while fetching user with ID {paramUserID}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def getUserByEmail(self, paramEmail):
        try:
            session = scoped_session(self.session_factory)
            user = session.query(User).filter(User.email == paramEmail).first()
            if user:
                return user
            return None
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while fetching user with Email {paramEmail}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def updateUserLastLogin(self, paramUserID, paramLastLogin):
        try:
            session = scoped_session(self.session_factory)
            user = session.query(User).filter(User.userID == paramUserID).first()

            if user is None:
                print(f"UserRepository: No user found with ID {paramUserID}")
                return
            user.lastLogin = paramLastLogin
            session.commit()
        except SQLAlchemyError as e:
            print(f"UserRepository: An error occurred while updating the last login for user ID {paramUserID}: {e}")
            session.rollback()
        finally:
            session.close()