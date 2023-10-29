import os
import time

import click
import rich.progress as rp
from litestar import Litestar
from litestar.plugins import CLIPluginProtocol
from rich.console import Console
from rich.table import Table

import SimplyTransport.lib.gtfs_importers as imp


def gtfs_directory_validator(dir: str, console: Console):
    if dir:
        if os.path.exists(dir) and os.path.isdir(dir):
            print("Using directory: " + dir)
        else:
            console.print(f"[red]Error: Directory '{dir}' does not exist.")
            return
    else:
        dir = "./gtfs_data/TFI/"
        console.print(f"No directory specified, using default of {dir}")

    return dir


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: click.Group) -> None:
        @cli.command(name="settings", help="Prints the current settings of the app")
        def settings():
            """Prints the current settings of the app"""

            from SimplyTransport.lib import settings

            env_settings = settings.BaseEnvSettings()
            console = Console()

            table = Table()
            table.add_column("Setting", style="cyan")
            table.add_column("Value")

            table.add_row("LITESTAR_APP", env_settings.LITESTAR_APP)
            if env_settings.DEBUG:
                debug_style = "green"
            else:
                debug_style = "red"
            table.add_row("Debug", str(env_settings.DEBUG), style=debug_style)
            table.add_row("Environment", env_settings.ENVIRONMENT)
            table.add_row("Database URL", env_settings.DB_URL)
            table.add_row("Log Level", env_settings.LOG_LEVEL)

            console.print(table)

        @cli.command(name="docs", help="Prints the documentation urls for the API")
        def docs(app: Litestar):
            """Prints the documentation urls for the API"""

            console = Console()
            base_url = "http://localhost:8000"  # TODO: Make this automatically get the base url
            docs_path = app.openapi_config.openapi_controller.path
            redoc_path = list(app.openapi_config.openapi_controller.redoc.paths)[0]
            swagger_path = list(app.openapi_config.openapi_controller.swagger_ui.paths)[0]
            elements_path = list(app.openapi_config.openapi_controller.stoplight_elements.paths)[
                0
            ]
            table = Table()
            table.add_column("Doc Type", style="cyan")
            table.add_column("URL")

            table.add_row("Default", f"{base_url}{docs_path}")
            table.add_row("Redoc", f"{base_url}{docs_path}{redoc_path}")
            table.add_row("Swagger", f"{base_url}{docs_path}{swagger_path}")
            table.add_row("Elements", f"{base_url}{docs_path}{elements_path}")

            console.print(table)

        @cli.command(name="importgtfs", help="Imports GTFS data into the database")
        @click.option("-dir", help="The directory containing the GTFS data to import")
        def importgtfs(dir: str):
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
                console.print(f"[red]Aborting import...")
                return

            files_to_import = [
                "agency.txt",
                "calendar.txt",
                "calendar_dates.txt",
                "routes.txt",
                "trips.txt",
            ]

            for file in files_to_import:
                if not (os.path.exists(dir) and os.path.isfile(dir + file)):
                    console.print(f"[red]Error: File '{file}' does not exist. Skipping...")
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
                    continue

                console.print(f"\nLoaded {importer} for {row_count} rows")
                with rp.Progress(
                    rp.SpinnerColumn(finished_text="✅"),
                    "[progress.description]{task.description}",
                    rp.TimeElapsedColumn(),
                ) as progress:
                    task = progress.add_task(f"[red]Clearing database table...", total=1)
                    importer.clear_table()
                    progress.update(task, advance=1)

                importer.import_data()

            finish: float = time.perf_counter()
            console.print(f"\n[blue]Finished import in {round(finish-start, 2)} second(s)")
