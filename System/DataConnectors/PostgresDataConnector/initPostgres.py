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
                    userID = 1,
                    email = email,
                    password = hashlib.sha256(password.encode('utf-8')).hexdigest(),
                    lastName = 'Last1',
                    firstName = 'First1',
                    role=UserRole.ADMIN
                    )

            availableApi1 = AvailableApi( availableApiID = 1,
                                    url = "https://finnhub.io/api/v1/quote?symbol=AAPL",
                                    name = "Finnhub Apple",
                                    subscriptionType = SubscriptionType.FREE,
                                    relevantFields = ["c", "d", "dp", "h", "l", "o", "pc", "t"])

            availableApi2 = AvailableApi( availableApiID = 2,
                                    url = "https://finnhub.io/api/v1/quote?symbol=IBM",
                                    name = "Finnhub IBM",
                                    subscriptionType = SubscriptionType.FREE,
                                    relevantFields = ["c", "d", "dp", "h", "l", "o", "pc", "t"])

            availableApi3 = AvailableApi( availableApiID = 3,
                                    url = "https://api.open-meteo.com/v1/forecast?latitude=48.6767637&longitude=10.152923&current=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,rain,cloud_cover,wind_speed_10m",
                                    name = "Weather Heidenheim",
                                    subscriptionType = SubscriptionType.FREE,
                                    relevantFields = ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "cloud_cover", "wind_speed_10m"])


            session.add(user)
            session.commit()
            
            session.add(availableApi1)
            session.add(availableApi2)
            session.add(availableApi3)
            session.commit()

        else:
            print("Environment variables USER_EMAIL or USER_PASSWORD are not set.")

    print("Database initialized.")
    session.close()


if __name__ == '__main__':
    initializePostgres()
