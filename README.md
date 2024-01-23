[![CI/CD](https://github.com/ANIALLATOR114/SimplyTransport/actions/workflows/tests_on_merge_main.yaml/badge.svg?branch=main)](https://github.com/ANIALLATOR114/SimplyTransport/actions/workflows/tests_on_merge_main.yaml)

# 🚌 SimplyTransport

- Litestar Python ASGI web app
- API & Website for real-time transport updates and schedules
- GTFS and GTFS-R data ingestor

## 📖 Content

- [About](#about)
- [API Docs](#api-documentation)
- [Web Interface](#web-interface)
- [CLI Interface](#cli-interface)
- [Contributing](CONTRIBUTING.md)

- [Installation](#installation)

  - [Running Locally](#running-locally)
  - [Running in Production](#running-in-production)

- [Development](#development)
  - [Project Structure](#project-structure)
    - [Controllers](#controllers)
    - [Domain](#domain)
    - [Services](#services)
    - [Lib](#lib)
    - [Templates](#templates)
  - [Database](#database)
    - [Migrations](#migrations)
- [Testing](#testing)
  - [Integration Tests](#integration-tests)
  - [Unit Tests](#unit-tests)
  - [Code Coverage](#code-coverage)

## About

> [!NOTE]
> The accuracy of the data is entirely the responsability of the transport providers

[GTFS Reference](https://gtfs.org/schedule/) The standard format for the transport data

[TFI Public GTFS Datasets](https://www.transportforireland.ie/transitData/PT_Data.html) The Irish governments GTFS data

[GTFS-R](https://developer.nationaltransport.ie/apis) The Irish governments Realtime data feeds. You cannot query this as you might expect, you must download the entire feed (rate limited to 1/min)

SimplyTransport is designed to continually request the GTFS-R feed as often as possible.
The static schedules can be updated as often as desired but typically a nightly update is sufficient.

## API Documentation

[Website Link](https://simplytransport.ie/apidocs)

[Redoc](https://simplytransport.ie/docs/redoc)

[Swagger](https://simplytransport.ie/docs/swagger)

[StopLight](https://simplytransport.ie/docs/elements#/)

[OpenAPI Json](https://simplytransport.ie/docs/openapi.json)

[OpenAPI Yaml](https://simplytransport.ie/docs/openapi.yaml)

- [x] Agencies
- [x] Stops
- [x] Routes
- [x] Calendar
- [x] CalendarDates
- [x] StopTimes
- [x] Trips
- [x] Shapes
- [x] Schedules
- [x] Realtime
- [ ] Realtime Vehicles
- [ ] StopFeatures

## Web Interface

- [x] Homepage
- [x] About
- [x] Stop
  - [x] Realtime
  - [x] Schedule
  - [x] Stop Features
- [x] Route
- [x] Trip
- [x] Search Page
  - [x] Stops
  - [x] Routes
- [ ] Maps

## CLI Interface

> [!NOTE]
> All commands are prefixed with `litestar`

This extends the standard litestar cli. You can view all the commands by just running `litestar`.

- [x] Application Settings `settings`
- [x] Documentation Links `docs`
- [x] GTFS Importer `importgtfs`
- [x] Realtime Updater `importrealtime`
- [x] Stop Feature Importer `importstopfeatures`
- [x] Create Database tables manually `create_tables`
- [x] Recreate all database indexes `recreate_indexes`

# Installation

> [!NOTE]
> This project was created using Python 3.11 and the following commands are for a linux cmd

First clone down the project in your desired directory

```
git clone https://github.com/ANIALLATOR114/SimplyTransport.git
```

Create a virtual environment inside the root directory of the project

```
python3 -m venv venv
```

Activate the virtual environment

```
source venv/scripts/activate
```

Install the dependencies in your virtual environment

```
pip install -r requirements.txt
```

Create a copy of .env.example and populate it with your environment variables

```
cp .env.example .env
```

Open the `.env` file and change the example variables for the following fields. You can set these to whatever you like as they will be unique to your local deployment.

Notice how the `POSTGRES_` variables map into the URL you're going to try and connect to. Docker-compose will create a DB using these variables for you.

```
# Database
DB_URL=postgresql+asyncpg://example2:example3@localhost:5432/example1
DB_URL_SYNC=postgresql+psycopg2://example2:example3@localhost:5432/example1
DB_ECHO=false

# Postgres Docker
POSTGRES_DB=example1
POSTGRES_USER=example2
POSTGRES_PASSWORD=example3
```

Once you have the variables above set please run the command in [Database](#database)

## Running Locally

You can run the app using the litestar run command for local development which will use a uvicorn worker to launch the app on 127.0.0.1:8000

When you run `litestar <command>` it will try and find the Litestar app to launch via the `.env` file. You shouldnt need to have changed this from the `.env.example`

```
litestar run
```

This will reload the app when changes are made for development convenience

```
litestar run --reload
```

The custom commands I've added to the app can be run using the litestar command in the same way

```
litestar settings
```

```
litestar docs
```

```
litestar importgtfs
```

```
litestar importrealtime
```

## Running in Production

You should use uvicorn directly to run the app in production and not litestar, this will allow you to configure the number of workers, ports etc

```
uvicorn SimplyTransport.app:create_app --port 8000 --env-file .env
```

Example configs are available for Supervisor and Nginx for hosting on Linux.
This allows you to run the app as a service and proxy requests to it from Nginx, Supervisor will manage the processess and restart them if they fail.
Once configured you can start the app under supervisor using the following command

```
supervisorctl start simplytransport
```

It is advisable to have nginx serve the static files for the app, you can do this by adding the following to your nginx config.
A similar line is already present in the example config as well as a robots.txt example

```
location /static {
    alias /path/to/SimplyTransport/static;
}
```

# Development

## Project Structure

This app is a Litestar Python ASGI web application, it's organised into controllers, domain, services, lib extensions and templates.

### Controllers

This is where the endpoints for the app are defined, these are the entry points for the API and the web interface.

Each controller will be injected with any services or repositories it requires to function.
Controllers should be kept as thin as possible, they should only be responsible for handling the request and returning a response.

The routing for each controller is configured in the `__init__.py` file in the controllers directory.
This file also controls the prefix for the routes, if schema generation is enabled and any auth requirements.

### Domain

This is where the models for the app are defined, these are the objects that are returned by the API and used in endpoints.

Most of these will be based closely on the GTFS data but some are custom objects which could be a transformation of the gtfs models.

Commonly these will have a SQLAlchemy model associated with them (should it require one).
Each model should have its own dedicated repository which is used to query the database for that object.

### Services

This is where more complicated logic is organised.

Services should be injected with any repositories they require to function.

Services will combine data from multiple repositories to create a more complex object or perform some logic.

### Lib

This is where any extensions to the app are defined.

This includes things like the database, the schema generator, logging, etc.

### Templates

This is where the templates for the web interface are defined.

These are jinja2 templates which are rendered by the controllers.

There is a base template which is extended by any other templates that define a distinct web page.

Partial templates are smaller templates that are returned with the intention to inject them into the calling template. HTMX is used to request and swap these partials in and out of the DOM.

## Database

This application expects a Postgres database to be available at the url specificed in the .env file.

There is a `docker-compose.yaml` available in the root directory of the project which will create the postgres database for you as well as a redis instance for caching.

```
docker-compose up -d
```

### Migrations

This application uses Alembic for migrations, you can create a new migration using the following command
You should be in the root directory

```
alembic revision --autogenerate -m "The name of my migration"
```

To apply the migration to your database use the following command

```
alembic upgrade head
```

# Testing

SimplyTransport has **Integration** and **Unit** tests implemented using pytest.

You can run the tests using the following command in the root directory.

There is a small test dataset of GTFS data in the tests directory which is used for consistent testing.

```
pytest
```

## Integration Tests

The integration tests use a test client to make requests to a test version of SimplyTransport.

Here is an example in `test_root.py`

```python
from litestar.testing import TestClient

def test_root_200(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to SimplyTransport" in response.text
```

## Unit Tests

The unit tests make heavy use of mocking to test the logic of the app in isolation as dependency injection is used throughout the core services.

Here is an example in `test_schedule_service.py`

```python
from unittest.mock import AsyncMock,
from SimplyTransport.domain.services.schedule_service import ScheduleService
from SimplyTransport.domain.enums import DayOfWeek

@pytest.mark.asyncio
async def test_get_schedule_on_stop_for_day_should_call_repository():
    # Arrange
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    stop_id = "stop_id"
    day = DayOfWeek.MONDAY

    # Act
    await schedule_service.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)

    # Assert
    schedule_repository.get_schedule_on_stop_for_day.assert_called_once_with(
        stop_id=stop_id, day=day
    )
```

In this example we specifically want to ensure that the `get_schedule_on_stop_for_day` method on the `schedule_repository` is called with the correct arguments and just one time.

## Code Coverage

Code coverage is measured using coverage, you can run the tests with coverage using the following command in the root directory.

```
coverage run -m pytest
```

You can then generate a report on your cmd using the following command

```
coverage report
```

You can also generate a html report using the following command

```
coverage html --show-contexts
```

This will generate a htmlcov directory in the root directory where you can open index.html to view the report in your browser.
