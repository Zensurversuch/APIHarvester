from repositories import userRepository, subscriptionRepository, availableApiRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from commonRessources.interfaces import UserRole, SubscriptionType
from commonRessources.logger import setLoggerLevel
import time
import hashlib
from os import getenv
from dbModels.models import Base, User, AvailableApi
import sqlalchemy.exc

# -------------------------- Environment Variables -----------------------------------------------------------------------------------------------------------------------------------
POSTGRES_URL = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@database/{getenv('POSTGRES_DB')}"

# --------------------------- Initializations -----------------------------------------------------------------------------------------------------------------------------------------
logger = setLoggerLevel("PostgresInitializer")
engine = create_engine(POSTGRES_URL)
userRepo = userRepository.UserRepository(engine)
subscriptionRepo = subscriptionRepository.SubscriptionRepository(engine)
availableApiRepo = availableApiRepository.AvailableApiRepository(engine)

def initializePostgres():
    """
    Initialize the PostgreSQL database. Creates the necessary tables and adds initial data into them.
    """
    logger.info("Initializing PostgreSQL DB")
    isDatabaseReady = False
    retries = 0
    max_retries = 20  # Set a maximum number of retries
    retry_interval = 2  # Time to wait between retries in seconds

    while not isDatabaseReady and retries < max_retries:
        logger.info(f"Trying to setup PostgreSQL (Attempt {retries + 1}/{max_retries})")
        try:
            Base.metadata.create_all(engine)
            isDatabaseReady = True
        except sqlalchemy.exc.OperationalError as e:
            logger.warning(f"PostgreSQL is unavailable - retrying in {retry_interval} seconds: {e}")
            retries += 1
            time.sleep(retry_interval)

    if not isDatabaseReady:
        print("Failed to connect to PostgreSQL after several attempts. Exiting.")
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    try:        # Add admin user and available APIs to the database
        if session.query(User).count() == 0:
            email = getenv('USER_EMAIL')
            password = getenv('USER_PASSWORD')
            if email and password:
                # Create the admin user
                user = User(
                    userID=1,
                    email=email,
                    password=hashlib.sha256(password.encode('utf-8')).hexdigest(),
                    lastName='Admin',
                    firstName='Admin',
                    role=UserRole.ADMIN
                )
                session.add(user)
                session.commit()
                print(f"Admin user {email} created.")
            else:
                print("Environment variables USER_EMAIL or USER_PASSWORD are not set.")
        else:
            print("Admin user already exists.")

        if session.query(AvailableApi).count()==0:      # New APIs have to be added here
            availableApi1 = AvailableApi(
                availableApiID=1,
                url="https://finnhub.io/api/v1/quote?symbol=AAPL",
                name="Finnhub Apple",
                apiTokenRequired=True,
                description="This Api returns the current Apple stock price via Finnhub",
                subscriptionType=SubscriptionType.FREE,
                relevantFields=["c", "d", "dp", "h", "l", "o", "pc", "t"]
            )
            availableApi2 = AvailableApi(
                availableApiID=2,
                url="https://finnhub.io/api/v1/quote?symbol=IBM",
                name="Finnhub IBM",
                apiTokenRequired=True,
                description="This Api returns the current IBM stock price via Finnhub",
                subscriptionType=SubscriptionType.FREE,
                relevantFields=["c", "d", "dp", "h", "l", "o", "pc", "t"]
            )
            availableApi3 = AvailableApi(
                availableApiID=3,
                url="https://api.open-meteo.com/v1/forecast?latitude=48.6767637&longitude=10.152923&current=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,rain,cloud_cover,wind_speed_10m",
                name="Weather Heidenheim",
                apiTokenRequired=False,
                description="This Api returns the current relevant weather data for heidenheim",
                subscriptionType=SubscriptionType.FREE,
                relevantFields=["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "cloud_cover", "wind_speed_10m"]
            )
            availableApi4 = AvailableApi(
                availableApiID=4,
                url="https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM",
                name="AlphaVantage IBM",
                apiTokenRequired=True,
                description="This Api returns the current IBM stock price via AlphaVantage",
                subscriptionType=SubscriptionType.FREE,
                relevantFields=["01. symbol", "02. open", "03. high", "04. low", "05. price", "06. volume", "07. latest trading day", "08. previous close", "09. change", "10. change percent"]
            )

            session.add(availableApi1)
            session.add(availableApi2)
            session.add(availableApi3)
            session.add(availableApi4)
            session.commit()
            print("APIs created and added to the database.")
        print("Database initialized.")
    except Exception as e:
        session.rollback()
        print(f"Error during initializing the PostgreSQL database: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    initializePostgres()
