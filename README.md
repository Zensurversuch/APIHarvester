# API Harvester

## Short Description
API Harvester allows periodic collection and visualization of data from pre-configured API endpoints. New APIs can be added by the admins to expand the plattform.

## Deployment
### Starting the application
Requirements:
Docker installed (https://docs.docker.com/get-docker/)

Procedure (the deployment process is completed with a single command):

1. Download the repository
```bash
git clone https://github.com/Zensurversuch/APIHarvester.git
```
2. Create the needed `.env` file as described [here](#setup-environment)
3. Create the needed `apikeys.txt` file as described [here](#api-keys-secrets)
4. Navigate to the folder (/System)
5. Open the console and execute the following command:
```bash
docker-compose up --build
```

### Restarting the complete application with deleting all the data
1. Open the console and execute the following command or press *CTRL+C*:
```bash
docker-compose down
```
2. Open Docker Desktop and delete the compose environment under Containers  
   Alternatively, this can be done via the command line. Open the console and run:
   ```bash
   docker-compose rm -f
   ```
3. Use Docker Desktop in order to delete the API-Harvester related volumes under Volumes.  
   You can also achieve this using the console with the following command:
   ```bash
   docker volume rm $(docker volume ls -q)
   ```
4. Delete the entries in the config.ini file which is located under [System\Scheduler\\.config\config.ini](System/Scheduler/.config/config.ini)
   If this is not done the System behaves wrong when starting it again
   (This has to be done because the entries in this file are related to the database subscription entries. And the database entries are deleted by deleting the volumes. The casual behaviour is that both entries are deleted through the frontend)


## Setup environment
### .env file

1. Create a `.env` file in the `System/` directory.

2. Add the following configuration variables:

    ```env
    JWT_SECRET_KEY=<jwt key>                  # Set the secret key for the JWT token
    INTERNAL_API_KEY=<apikeyXY>               # Set an API_KEY here, which is used in order for the intern service-service API's

    ENV=<prod | dev>                          # Environment mode: 'dev' for development, 'prod' for production

    #PostgreSQL variables
    POSTGRES_PASSWORD=<password>              # Set the password for your PostgreSQL database
    USER_EMAIL= <e-mail>                      # Set the E-Mail for the first Application User (optional)
    USER_PASSWORD = <password>                # Set the Password for the first Application User (optional)

    # InfluxDB variables
    INFLUXDB_ADMIN_USER=<admin user name>           # Admin username for accessing InfluxDb
    INFLUXDB_ADMIN_PASSWORD=<admin user password>   # Admin password for accessing InfluxDb
    INFLUXDB_ORG=apiHarvester                       # Name of the InfluxDb organization
    INFLUXDB_TOKEN=<token>                          # authentificationtoken for InfluxDb

    MAX_NUMBER_WORKERS=<number>   # The amount of worker containers has to be set here
    ```

### API Keys secrets
Create a file containing all the required API keys as a key-value file. It should be located under `System/apikeys.txt` and formatted as follows:  

``` text
FINNHUB_KEY=<finnhub api key>
ALPHAVANTAGE_KEY=<alpha vantage api key>
```
**_NOTE:_** If you add a new API by adding the data in the [System\DataConnectors\PostgresDataConnector\initPostgres.py](initPostgres.py) script make sure you do the following:
* if you use 'WeatherAndStarApi XY' as the APIName, the entry in apikeys.txt has to be WEATHERANDSTARAPI=KeyXy  (The point is that while fetching the API the workers search the Key in the apikeys.txt by using the ApiName in the database until space)
* if the new added api needs a Key you have to adapt the method fetchApi() [System\Worker\fetchScripts\fetchApis.py](fetchApis.py) because different APIs have other names for the API key parameter. Therefore add the Api in the switch case statement and add how the API key parameter is named:
```python
if availableApiName == 'FINNHUB':                     # Different APIs require different query parameters in order to pass the API token
  response = requests.get(f"{url}&token={apiToken}")
elif availableApiName == 'ALPHAVANTAGE':
  response = requests.get(f"{url}&apikey={apiToken}")
```

## Current fetchable API's
* Weather API [open-meteo](https://open-meteo.com/)
  * 10'000 API calls per day
  * Free to use for non-commercial
  * No API key needed

* Stocks and exchange rates [Finnhub](https://finnhub.io/)
  * free 60 API calls/minute.
  * API key needed
  * There's a function which returns the needed symbol (id which represents the name of the stock) [here](https://finnhub.io/docs/api/symbol-search)
  * returns: 
  ``` json
    {
    "c": 183.31,  // Current Price - Latest trading price of the stock.
    "d": -5.81,   // Change - Absolute change from the previous close.
    "dp": -3.0721, // Change Percent - Percentage change from the previous close.
    "h": 185.255, // High - Highest price of the day.
    "l": 181.81,  // Low - Lowest price of the day.
    "o": 184.55,  // Open - Price at market open.
    "pc": 189.12, // Previous Close - Price at the previous market close.
    "t": 1722888002 // Timestamp - Unix timestamp of the last update.
    }
  ```


* Stock market API [ALPHA Vantage](https://www.alphavantage.co/)
  * free 25 calls per day
  * API key needed
  * There's a function which returns the needed symbol (id which represents the name of the stock) [here](https://www.alphavantage.co/documentation/#symbolsearch)  
  We may give the option that the client is able to fetch all the stocks he wants, in the future

### API's which will be added in the future:
- At the moment none

## Features
- User registration
- Selection from a list of pre-configured APIs.
- Administrators can expand the API list.
- Users can select APIs to fetch data from, specifying the fetch frequency. These API queries are executed periodically, and data is stored in a Time-Series Database (InfluxDB).
- Dashboard for visualization.

## Git Rules
- **Branching**: Use the format `Storynumber-Storyname` or `Tasknumber-Storyname` or `Storynumber-Tasknumber-Storyname`
- **Commit**: Format: `Storynumber-Tasknumber-Comment`. If no Storynumber is available (Storyless Task) use the Format: `Tasknumber-Comment`
- **Merge**: Merge Commit Strategy; All commit messages are retained. No direct commits to `Main`; changes must go through Pull Requests (configured via settings). Delete feature branches after merging.
- **Release**: A release always follows Sprint Review.
- **Pull Request**: Requires approval from at least one developer for the latest pull request state.

