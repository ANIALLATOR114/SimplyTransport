from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import MetaData, text
from .database import engine, session, async_engine
from .timescale_database import async_timescale_engine


async def create_database() -> None:
    """
    Creates the database tables.

    This function creates all the tables defined in the SQLAlchemy models
    using the metadata and the database connection from the current session.

    Raises:
        ConnectionRefusedError: If the database connection is refused.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(UUIDBase.metadata.create_all)
    except ConnectionRefusedError as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {async_engine.url}\n"
        )
        raise e


def create_database_sync() -> None:
    """
    Creates the database tables synchronously.

    This function creates all the tables defined in the SQLAlchemy models
    using the metadata and the database connection from the current session.

    Raises:
        ConnectionRefusedError: If the database connection is refused.
    """
    try:
        UUIDBase.metadata.create_all(bind=session.bind)
    except ConnectionRefusedError as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {engine.url}\n"
        )
        raise e


def recreate_indexes(table_name: str | None = None):
    """Recreate all indexes

    Args:
        table_name (str | None): The name of the table to recreate indexes for. If None, indexes will be recreated for all tables.

    """
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if table_name is None:
        # recreate index on every table
        for table_name in metadata.tables:
            table = metadata.tables[table_name]
            indexes = list(table.indexes)
            for index in indexes:
                index.drop(bind=engine)
            for index in indexes:
                index.create(bind=engine)
    else:
        table = metadata.tables[table_name]
        indexes = list(table.indexes)
        for index in indexes:
            index.drop(bind=engine)
        for index in indexes:
            index.create(bind=engine)


async def test_database_connections():
    """
    Test the connection to the databases.

    Raises:
        Exception: If the database connection is refused.
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {async_engine.url}\n"
        )
        raise e
    
    try:
        async with async_timescale_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        print(e)
        print(
            f"\nTimescale Database connection refused. Please ensure the database is running and accessible.\nURL: {async_timescale_engine.url}\n"
        )
        raise e
