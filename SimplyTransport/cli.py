import json
import os
import time
import asyncio
import functools

import geojson
import click
import rich.progress as rp
from litestar import Litestar
from litestar.plugins import CLIPluginProtocol
from rich.console import Console
from rich.table import Table
from .lib.cache import provide_redis_service
from .lib.cache_keys import CacheKeys

import SimplyTransport.lib.gtfs_importers as imp
from SimplyTransport.lib.db import services as db_services
from .lib.gtfs_realtime_importers import RealTimeImporter, RealTimeVehiclesImporter
from .lib.stop_features_importer import StopFeaturesImporter
from .domain.events.repo import create_event_with_session, provide_event_repo
from .domain.events.event_types import EventType
from .lib.db.database import async_session_factory


DEFAULT_GTFS_DIRECTORY = "./gtfs_data/TFI/"


def gtfs_directory_validator(directory: str | None, console: Console):
    if directory:
        if os.path.exists(directory) and os.path.isdir(directory):
            print("Using directory: " + directory)
        else:
            console.print(f"[red]Error: Directory '{directory}' does not exist.")
            raise click.Abort()
    else:
        directory = DEFAULT_GTFS_DIRECTORY
        console.print(f"No directory specified, using default of {directory}")

    return directory


# https://github.com/pallets/click/issues/2033
def make_sync(func):
    """Decorator to run async functions in a sync context"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: click.Group) -> None:
        @cli.command(name="settings", help="Prints the current settings of the app")
        def settings():
            """Prints the current settings of the app"""

            from SimplyTransport.lib import settings

            console = Console()

            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value")

            table.add_row("LITESTAR_APP", settings.app.LITESTAR_APP)
            if settings.app.DEBUG:
                debug_style = "green"
            else:
                debug_style = "red"

            table.add_row("Debug", str(settings.app.DEBUG), style=debug_style)
            table.add_row("Environment", settings.app.ENVIRONMENT)
            table.add_row("Database URL", settings.app.DB_URL)
            table.add_row("Database SYNC URL", settings.app.DB_URL_SYNC)
            table.add_row("Database Echo", str(settings.app.DB_ECHO))
            table.add_row("Log Level", settings.app.LOG_LEVEL)

            console.print(table)

        @cli.command(name="docs", help="Prints the documentation urls for the API")
        def docs(app: Litestar):
            """Prints the documentation urls for the API"""

            console = Console()
            base_url = "http://localhost:8000"  # TODO: Make this automatically get the base url
            docs_path = app.openapi_config.openapi_controller.path
            redoc_path = list(app.openapi_config.openapi_controller.redoc.paths)[0]
            swagger_path = list(app.openapi_config.openapi_controller.swagger_ui.paths)[0]
            elements_path = list(app.openapi_config.openapi_controller.stoplight_elements.paths)[0]
            rapidoc_path = list(app.openapi_config.openapi_controller.rapidoc.paths)[0]

            table = Table()
            table.add_column("Doc Type", style="cyan")
            table.add_column("URL")

            table.add_row("Default", f"{base_url}{docs_path}")
            table.add_row("Redoc", f"{base_url}{docs_path}{redoc_path}")
            table.add_row("Swagger", f"{base_url}{docs_path}{swagger_path}")
            table.add_row("Elements", f"{base_url}{docs_path}{elements_path}")
            table.add_row("Rapidoc", f"{base_url}{docs_path}{rapidoc_path}")

            console.print(table)

        @cli.command(name="importgtfs", help="Imports GTFS data into the database")
        @click.option("-dir", help="Override the directory containing the GTFS data to import")
        @make_sync
        async def importgtfs(dir: str):
            """Imports GTFS data into the database"""

            start: float = time.perf_counter()
            console = Console()
            console.print("Importing GTFS data...")

            dir = gtfs_directory_validator(dir, console)

            dir_path = dir.split("/")
            dataset = dir_path[-2]
            response = click.prompt(
                f"\nYou are about to import this dataset and assign it to '{dataset}'. Press 'y' to continue, anything else to abort: ",
                type=str,
                default="",
                show_default=False,
            )
            if response != "y":
                console.print("[red]Aborting import...")
                return

            files_to_import = [
                "agency.txt",
                "calendar.txt",
                "calendar_dates.txt",
                "routes.txt",
                "stops.txt",
                "trips.txt",
                "stop_times.txt",
                "shapes.txt",
            ]
            attributes_of_total_rows = {}

            total_time_taken = 0.0
            start = time.perf_counter()

            for file in files_to_import:
                file_start = time.perf_counter()
                if not (os.path.exists(dir) and os.path.isfile(dir + file)):
                    console.print(f"[red]Error: File '{file}' does not exist. Skipping...")
                    attributes_of_total_rows[file.replace(".txt", "")] = {
                        "time_taken(s)": 0,
                        "row_count": 0,
                        "error": f"File '{file}' does not exist.",
                    }
                    continue

                generic_importer = imp.GTFSImporter(file, dir)
                reader = generic_importer.get_reader()
                row_count = generic_importer.get_row_count()
                try:
                    importer = imp.get_importer_for_file(file, reader, row_count, dataset)
                except ValueError:
                    console.print(
                        f"\n[red]Error: File '{file}' does not have a supported importer. Skipping..."
                    )
                    attributes_of_total_rows[file.replace(".txt", "")] = {
                        "time_taken(s)": 0,
                        "row_count": row_count,
                        "error": f"File '{file}' does not have a supported importer.",
                    }
                    continue

                console.print(f"\nLoaded {importer} for {row_count} rows")
                with rp.Progress(
                    rp.SpinnerColumn(finished_text="✅"),
                    "[progress.description]{task.description}",
                    rp.TimeElapsedColumn(),
                ) as progress:
                    task = progress.add_task("[red]Clearing database table...", total=1)
                    importer.clear_table()
                    progress.update(task, advance=1)

                if file in ["stop_times.txt", "shapes.txt", "trips.txt"]:
                    await importer.import_data()
                else:
                    importer.import_data()

                finish = time.perf_counter()
                time_taken = round(finish - file_start, 2)
                total_time_taken += time_taken

                attributes_of_total_rows[file.replace(".txt", "")] = {
                    "time_taken(s)": time_taken,
                    "row_count": row_count,
                }

            attributes = {
                "dataset": dataset,
                "totals": attributes_of_total_rows,
                "total_time_taken(s)": round(total_time_taken, 2),
            }

            await create_event_with_session(
                EventType.GTFS_DATABASE_UPDATED,
                "GTFS static data updated with latest schedules",
                attributes,
            )

            redis_service = provide_redis_service()
            await redis_service.delete_keys(CacheKeys.STOP_MAP_DELETE_ALL_KEY_TEMPLATE)
            await redis_service.delete_keys(CacheKeys.ROUTE_MAP_DELETE_ALL_KEY_TEMPLATE)
            await redis_service.delete_keys(CacheKeys.SCHEDULE_DELETE_ALL_KEY_TEMPLATE)

            console.print(f"\n[blue]Finished import in {round(finish-start, 2)} second(s)")

        @cli.command(name="importrealtime", help="Imports GTFS realtime data into the database")
        @click.option("-url", help="Override the default URL for the GTFS realtime data")
        @click.option("-apikey", help="Override the default API key for the GTFS realtime data")
        @click.option("-dataset", help="Override the default dataset that the data will be saved against")
        @make_sync
        async def importrealtime(url: str, apikey: str, dataset: str):
            """Imports GTFS realtime data into the database"""

            start: float = time.perf_counter()
            console = Console()
            console.print("Importing GTFS realtime data...")

            from SimplyTransport.lib import settings

            if url:
                realtime_url = url
                console.print(f"\nOverriding URL: {realtime_url}")
            else:
                realtime_url = settings.app.GTFS_TFI_REALTIME_URL

            if apikey:
                realtime_apikey = apikey
                console.print(f"\nOverriding API key: {realtime_apikey}")
            else:
                realtime_apikey = settings.app.GTFS_TFI_API_KEY_1

            if dataset:
                realtime_dataset = dataset
                console.print(f"\nOverriding dataset: {realtime_dataset}")
            else:
                realtime_dataset = settings.app.GTFS_TFI_DATASET

            importer = RealTimeImporter(url=realtime_url, api_key=realtime_apikey, dataset=realtime_dataset)

            console.print(f"\nImporting using dataset: {realtime_dataset} from {realtime_url}")

            data = importer.get_data()

            if data is None:
                console.print(
                    "[red]Error: No data returned from API, either response was not 200 or JSON was invalid."
                )
                return

            console.print(f"\n{len(data['entity'])} entities returned from API")

            importer.clear_table_stop_trip()
            console.print("\nImporting Stop Times")
            total_stop_times = importer.import_stop_times(data)

            console.print("\nImporting Trips")
            total_trips = importer.import_trips(data)

            finish: float = time.perf_counter()
            attributes = {
                "dataset": realtime_dataset,
                "total_trips": total_trips,
                "total_stop_times": total_stop_times,
                "time_taken(s)": round(finish - start, 2),
            }
            await create_event_with_session(
                EventType.REALTIME_DATABASE_UPDATED,
                "Realtime database updated with new realtime information",
                attributes,
            )

            console.print(f"\n[blue]Finished import in {round(finish-start, 2)} second(s)")

        @cli.command(
            name="importrealtimevehicles", help="Imports GTFS realtime vehicle data into the database"
        )
        @click.option("-url", help="Override the default URL for the GTFS realtime vehicle data")
        @click.option("-apikey", help="Override the default API key for the GTFS realtime vehicle data")
        @click.option("-dataset", help="Override the default dataset that the data will be saved against")
        @make_sync
        async def importrealtimevehicles(url: str, apikey: str, dataset: str):
            """Imports GTFS realtime data into the database"""

            start: float = time.perf_counter()
            console = Console()
            console.print("Importing GTFS realtime data...")

            from SimplyTransport.lib import settings

            if url:
                realtime_url = url
                console.print(f"\nOverriding URL: {realtime_url}")
            else:
                realtime_url = settings.app.GTFS_TFI_REALTIME_VEHICLES_URL

            if apikey:
                realtime_apikey = apikey
                console.print(f"\nOverriding API key: {realtime_apikey}")
            else:
                realtime_apikey = settings.app.GTFS_TFI_API_KEY_2

            if dataset:
                realtime_dataset = dataset
                console.print(f"\nOverriding dataset: {realtime_dataset}")
            else:
                realtime_dataset = settings.app.GTFS_TFI_DATASET

            importer = RealTimeVehiclesImporter(
                url=realtime_url, api_key=realtime_apikey, dataset=realtime_dataset
            )

            console.print(f"\nImporting using dataset: {realtime_dataset} from {realtime_url}")

            data = importer.get_data()

            if data is None:
                console.print(
                    "[red]Error: No data returned from API, either response was not 200 or JSON was invalid."
                )
                return

            console.print(f"\n{len(data['entity'])} entities returned from API")

            importer.clear_table_vehicles()
            console.print("\nImporting Vehicles")
            total_vehicles = importer.import_vehicles(data)

            finish: float = time.perf_counter()
            attributes = {
                "dataset": realtime_dataset,
                "total_vehicles": total_vehicles,
                "time_taken(s)": round(finish - start, 2),
            }
            await create_event_with_session(
                EventType.REALTIME_VEHICLES_DATABASE_UPDATED,
                "Realtime vehicles database updated with new realtime information",
                attributes,
            )

            redis_service = provide_redis_service()
            await redis_service.delete_keys(CacheKeys.STOP_MAP_DELETE_ALL_KEY_TEMPLATE)

            console.print(f"\n[blue]Finished import in {round(finish-start, 2)} second(s)")

        @cli.command(name="create_tables", help="Creates the database tables")
        def create_tables():
            """Creates the database tables"""

            console = Console()
            console.print("Creating database tables...")

            db_services.create_database_sync()

        @cli.command(name="importstopfeatures", help="Imports stop features into the database")
        @click.option("-dir", help="Override the directory containing the stop feature data to import")
        @make_sync
        async def importstopfeatures(dir: str):
            """Imports stop features into the database"""

            start: float = time.perf_counter()
            console = Console()
            console.print("Importing stop features data...")

            dir = gtfs_directory_validator(dir, console)

            dir_path = dir.split("/")
            dataset = dir_path[-2]
            response = click.prompt(
                f"\nYou are about to import this dataset and assign it to '{dataset}'. Press 'y' to continue, anything else to abort: ",
                type=str,
                default="",
                show_default=False,
            )
            if response != "y":
                console.print("[red]Aborting import...")
                return

            def geojson_cleaner(filename: str) -> geojson.FeatureCollection:
                console.print(f"Cleaning {filename}...")

                with open(filename, "r", encoding="utf8") as f:
                    data = json.load(f)

                # Convert the coordinates to numbers from strings
                # This is needed because geojson doesn't support floats and for some TFI reason thats what the data is formatted with
                for feature in data["features"]:
                    feature["geometry"]["coordinates"] = [
                        float(coord) for coord in feature["geometry"]["coordinates"]
                    ]

                json_string = json.dumps(data)

                # Some data has double quotes around booleans, this is invalid so we need to replace them
                json_string = json_string.replace('"False"', "false").replace('"True"', "true")

                return geojson.loads(json_string)

            console.print("\nReading files and cleaning data...")
            stops = geojson_cleaner(f"{dir}stops.geojson")
            poles = geojson_cleaner(f"{dir}poles.geojson")
            shelters = geojson_cleaner(f"{dir}shelters.geojson")
            rtpis = geojson_cleaner(f"{dir}rtpi.geojson")

            console.print("\nImporting stop features...")
            importer = StopFeaturesImporter(
                dataset=dataset, stops=stops, poles=poles, shelters=shelters, rtpis=rtpis
            )

            importer.clear_database()

            stop_feature_attributes = importer.import_stop_features()

            finish: float = time.perf_counter()

            attributes = {
                "stop_features": stop_feature_attributes,
                "dataset": dataset,
                "time_taken(s)": round(finish - start, 2),
            }

            await create_event_with_session(
                EventType.STOP_FEATURES_DATABASE_UPDATED,
                "Stop features database updated with latest stop features",
                attributes,
            )

            console.print(f"\n[blue]Finished import in {round(finish-start, 2)} second(s)")

        @cli.command(name="recreate_indexes", help="Recreates the indexes on a given table")
        @click.option("-table", help="The table to recreate the indexes on")
        def recreate_indexes(table: str = None):
            """Recreates the indexes on a given table"""

            console = Console()
            console.print("Recreating indexes...")
            if table is None:
                console.print("[yellow]No table specified to recreate indexes on from the -table argument")
                response = click.prompt(
                    "\nYou are about to recreate indexes on all tables. Press 'y' to continue, anything else to abort: ",
                    type=str,
                    default="",
                    show_default=False,
                )
                if response != "y":
                    console.print("[red]Aborting recreate indexes...")
                    return
            else:
                console.print(f"Recreating indexes on table {table}")
                response = click.prompt(
                    f"\nYou are about to recreate indexes on table {table}. Press 'y' to continue, anything else to abort: ",
                    type=str,
                    default="",
                    show_default=False,
                )
                if response != "y":
                    console.print("[red]Aborting recreate indexes...")
                    return

            start = time.perf_counter()

            db_services.recreate_indexes(table)

            finish = time.perf_counter()
            console.print(f"\n[blue]Finished recreating indexes in {round(finish-start, 2)} second(s)")

        @cli.command(name="cleanupevents", help="Cleans up expired events from the database")
        @click.option("-event", help="Cleanup just a specific event type")
        @make_sync
        async def cleanupevents(event: str = None):
            """Cleans up expired events from the database"""

            start: float = time.perf_counter()
            console = Console()
            console.print("Cleaning up events...")

            if event:
                try:
                    event = EventType(event)
                except ValueError:
                    console.print(f"[red]Error: Event type '{event}' does not exist.")
                    return

            number_deleted = 0
            async with async_session_factory() as session:
                event_repo = await provide_event_repo(session)
                if event:
                    console.print(f"\nCleaning up just event type: {event}")
                    number_deleted = await event_repo.cleanup_events(event_type=event)
                else:
                    console.print("\nCleaning up all events")
                    number_deleted = await event_repo.cleanup_events()

            finish: float = time.perf_counter()
            console.print(f"\n[blue]Deleted {number_deleted} events")
            console.print(f"\n[blue]Finished cleanup in {round(finish-start, 2)} second(s)")

        @cli.command(name="flushredis", help="Flushes the Redis cache")
        @make_sync
        async def flushredis():
            """Flushes the Redis cache"""

            console = Console()
            console.print("Flushing the Redis cache...")

            redis_service = provide_redis_service()

            total_keys = await redis_service.count_all_keys()
            console.print(f"\nTotal keys in the Redis cache: {total_keys}")

            await redis_service.delete_all_keys()
            console.print("\n[blue]Finished flushing the Redis cache")
