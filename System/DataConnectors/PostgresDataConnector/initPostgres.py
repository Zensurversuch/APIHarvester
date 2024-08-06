from repositories import userRepository, subscriptionRepository, availableApiRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from interfaces import UserRole, ApiStatusMessages, SubscriptionStatus, SubscriptionType
import time
import hashlib
from os import getenv
from dbModels.models import Base, User, Subscription, AvailableApi

POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"

# Postgres Init
engine = create_engine(POSTGRES_URL)
userRepo = userRepository.UserRepository(engine)
subscriptionRepo = subscriptionRepository.SubscriptionRepository(engine)
availableApiRepo = availableApiRepository.AvailableApiRepository(engine)



def initializePostgres():
    isDatabaseReady = False
    while not isDatabaseReady:
        try:
            Base.metadata.create_all(engine)

            Session = sessionmaker(bind=engine)
            session = Session()
            isDatabaseReady = True
        except Exception as e:
            print(f"PostgreSQL is unavailable - retrying in 1 second: {e}")
            time.sleep(1)

    #add admin user during initial setup
    if session.query(User).count() == 0:
        email = getenv('USER_EMAIL')
        password = getenv('USER_PASSWORD')
        if email and password:
        # Create the admin user
            user = User(
            email = email,
            password = hashlib.sha256(password.encode('utf-8')).hexdigest(),
            lastName = 'Last1',
            firstName = 'First1',
            role=UserRole.ADMIN
            )

            availableApi = AvailableApi( availableApiID = 1,
                                    url = "https://finnhub.io/api/v1/",
                                    description = "Stocks and Exchange Rates",
                                    subscriptionType = SubscriptionType.FREE,
                                    relevantFields = ["c", "d", "dp", "h", "l", "o", "pc", "t"])

            availableApi2 = AvailableApi( availableApiID = 2,
                                    url = "test",
                                    description = "Something",
                                    subscriptionType = SubscriptionType.FREE,
                                    relevantFields = ["bla", "foo"])

            subscription = Subscription( userID = 1,
                                         availableApiID = 1,
                                         interval = 5, 
                                         status = SubscriptionStatus.ACTIVE)

            
            subscription2 = Subscription( userID = 1,
                                         availableApiID = 1,
                                         interval = 5, 
                                         status = SubscriptionStatus.INACTIVE)  
            
            session.add(user)
            session.add(availableApi)
            session.add(availableApi2)
            session.commit()
            session.add(subscription)
            session.add(subscription2)
            session.commit()
            print("Admin user created successfully.")
        else:
            print("Environment variables USER_EMAIL or USER_PASSWORD are not set.")

    print("Database initialized.")
    session.close()


if __name__ == '__main__':
    initializePostgres()
