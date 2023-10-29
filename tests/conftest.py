import pytest
from litestar.testing import TestClient
from litestar import Litestar
from collections import abc


@pytest.fixture()
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


@pytest.fixture()
def client(app: Litestar) -> abc.Iterator[TestClient]:
    """Client instance attached to app.

    Args:
        app: The app for testing.

    Returns:
        Test client instance.
    """
    with TestClient(app=app) as c:
        yield c
