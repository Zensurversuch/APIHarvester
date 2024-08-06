# API Harvester

## Short Description
API Harvester allows periodic collection and visualization of data from pre-configured API endpoints. New APIs can be easily added to expand the platform.

## Setup environment
### .env file

1. Create a `.env` file in the `System/` directory.

2. Add the following configuration variables:

    ```env
    JWT_SECRET_KEY=<jwt key>                  # Set the secret key for the JWT token
    ENV=<prod | dev>                          # Environment mode: 'dev' for development, 'prod' for production

    #PostgreSQL variables
    POSTGRES_PASSWORD=<password>                    # Set the password for your PostgreSQL database
    USER_EMAIL= <e-mail>                      # Set the E-Mail for the first Application User (optional)
    USER_PASSWORD = <password>                # Set the Password for the first Application User (optional)

    # InfluxDB variables
    INFLUXDB_ADMIN_USER=<admin user name>
    INFLUXDB_ADMIN_PASSWORD=<admin user password>
    INFLUXDB_ORG=apiHarvester
    INFLUXDB_TOKEN=<token>
    ```

### API Keys secrets
Create a file containing all the required API keys as a key-value file. It should be located under `System/apikeys.txt` and formatted as follows:

``` text
WEATHER_KEY=<weather api key>
STOCKS_KEY=<stock market api key>
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




## Features
- Selection from a list of pre-configured APIs.
- Administrators can expand the API list.
- Users can select APIs to fetch data from, specifying the fetch frequency. These API queries are executed periodically, and data is stored in a Time-Series Database (InfluxDB).
- Users can set threshold values. If an API value crosses these thresholds, it's stored in a separate database (PostgreSQL). Upon subsequent logins, users can see when these thresholds were crossed based on timestamps and their last login.
- Dashboard for visualization and threshold monitoring.

## Git Rules
- **Branching**: Use the format `Storynumber-Storyname` or `Tasknumber-Storyname` or `Storynumber-Tasknumber-Storyname`
- **Commit**: Format: `Storynumber-Tasknumber-Comment`. If no Storynumber is available (Storyless Task) use the Format: `Tasknumber-Comment`
- **Merge**: Merge Commit Strategy; All commit messages are retained. No direct commits to `Main`; changes must go through Pull Requests (configured via settings). Delete feature branches after merging.
- **Release**: A release always follows Sprint Review.
- **Pull Request**: Requires approval from at least one developer for the latest pull request state.

