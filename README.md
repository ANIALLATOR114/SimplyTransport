[![CI/CD](https://github.com/ANIALLATOR114/SimplyTransport/actions/workflows/tests_on_merge_main.yaml/badge.svg?branch=main)](https://github.com/ANIALLATOR114/SimplyTransport/actions/workflows/tests_on_merge_main.yaml)

# SimplyTransport

SimplyTransport is...

- a Litestar Python ASGI web application
- a peformant async API and Website providing Transport information and Realtime updates.
- an ingestor for GTFS and GTFS-R data, transforming and returning the data in more intuitive structures
<hr>

### Content

- [API Docs](#api-documentation)
- [Web Interface](#web-interface)
- [CLI Interface](#cli-interface)
- [About](#about)
- [Development](#development)
  - [Installation](#installation)
  - [Database](#database)
  - [Running](#running)

## API Documentation

[Redoc](docs/redoc)

[Swagger](docs/swagger)

[Elements](docs/elements)

_**- WIP**_

- [x] Agencies
- [x] Stops
- [x] Routes
- [x] Calendar
- [x] CalendarDates
- [x] StopTimes
- [x] Trips
- [x] Shapes
- [ ] Realtime
  - [ ] Stop
  - [ ] Route
  - [ ] Vehicles

## Web Interface

_**- WIP**_

- [x] Homepage
- [ ] About
- [ ] Stop
- [ ] Route
- [ ] Search Page
  - [ ] Stops
  - [ ] Routes

## CLI Interface

_**- WIP**_

> [!NOTE]
> All commands are prefixed with `litestar`

- [x] Application Settings `settings`
- [x] Documentation Links `docs`
- [x] GTFS Importer `importgtfs`
- [ ] Realtime Updater `realtime-update`

## About

_**- WIP**_

> [!NOTE]
> The accuracy of the data is entirely the responsability of the transport providers

[GTFS Reference](https://gtfs.org/schedule/) The standard format for the transport data

[TFI Public GTFS Datasets](https://www.transportforireland.ie/transitData/PT_Data.html) The Irish governments GTFS data

[GTFS-R](https://developer.nationaltransport.ie/apis) The Irish governments Realtime data feeds. You cannot query this as you might expect, you must download the entire feed (rate limited to 1/min)

<br>

# Development

## Installation

> [!NOTE]
> This project was created using Python 3.11 and the following commands are for a linux cmd

First clone down the project in your desired directory

```
git clone https://github.com/ANIALLATOR114/SimplyTransport.git
```

Second create a virtual environment inside the root directory of the project

```
python3 -m venv /venv
```

Third install the dependencies to your virtual environment

```
pip install -r requirements.txt
```

Fourth create a copy of .env.example and populate it with your environment variables

```
cp .env.example .env
```

## Database

This application expects a Postgres database to be available at the url specificed in the .env file
There is a docker-compose.yaml available in the root directory of the project which will create a postgres database for you

```
docker-compose up -d
```

## Running

You can run the app using the litestar run command which will use a uvicorn worker to launch the app on 127.0.0.1:8000

```
litestar run
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
