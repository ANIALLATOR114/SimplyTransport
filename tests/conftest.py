import pytest
from litestar.testing import AsyncTestClient, TestClient
from collections import abc
from litestar import Litestar
import click
from click.testing import CliRunner
from SimplyTransport.cli import CLIPlugin


@pytest.fixture(scope="session")
def app() -> Litestar:
    """Always use this `app` fixture and never do `from app.main import app`
    inside a test module. We need to delay import of the `app.main` module
    until as late as possible to ensure we can mock everything necessary before
    the application instance is constructed.

    Returns:
        The application instance.
    """
    # don't want main imported until everything patched.
    from SimplyTransport.app import create_app

    return create_app()


@pytest.fixture(scope="session")
def async_client(app: Litestar) -> AsyncTestClient:
    return AsyncTestClient(app=app)


@pytest.fixture(scope="session")
def client(app: Litestar) -> abc.Iterator[TestClient]:
    """Client instance attached to app.

    Args:
        app: The app for testing.

    Returns:
        Test client instance.
    """
    with TestClient(app=app) as c:
        yield c


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def cli_group() -> click.Group:
    cli = CLIPlugin()
    group = click.Group()
    cli.on_cli_init(group)
    return group