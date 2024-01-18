import SimplyTransport.lib.db.database as _db
from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import MetaData
from SimplyTransport.lib.db.database import engine


async def create_database() -> None:
    try:
        async with _db.sqlalchemy_config.get_engine().begin() as conn:
            await conn.run_sync(UUIDBase.metadata.create_all)
    except ConnectionRefusedError as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {_db.sqlalchemy_config.get_engine().url}\n"
        )
        raise e


def create_database_sync() -> None:
    try:
        UUIDBase.metadata.create_all(bind=_db.session.bind)
    except ConnectionRefusedError as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {_db.sqlalchemy_config.get_engine().url}\n"
        )
        raise e


def recreate_indexes(table_name: str | None = None):
    """Recreate all indexes"""

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
