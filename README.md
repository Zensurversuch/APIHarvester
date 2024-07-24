# API Harvester

## Short Description
API Harvester allows periodic collection and visualization of data from pre-configured API endpoints. New APIs can be easily added to expand the platform.

## Setup

1. Create a `.env` file in the `System/` directory.

2. Add the following configuration variables:

    ```env
    POSTGRES_PW=<password>                    # Set the password for your PostgreSQL database
    JWT_SECRET_KEY=<jwt key>                  # Set the secret key for the JWT token
    ENV=<prod | dev>                          # Environment mode: 'dev' for development, 'prod' for production
    USER_EMAIL= <e-mail>                      # Set the E-Mail for the first Application User (optional)
    USER_PASSWORD = <password>                # Set the Password for the first Application User (optional)
    ```


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

