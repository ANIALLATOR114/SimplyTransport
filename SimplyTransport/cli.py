from litestar.plugins import CLIPluginProtocol
from litestar import Litestar
from click import Group
from rich.console import Console
from rich.table import Table


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.command()
        def settings():
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

        @cli.command()
        def docs(app: Litestar):
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
