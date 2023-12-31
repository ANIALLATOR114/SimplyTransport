import SimplyTransport.lib.db.database as _db
from litestar.contrib.sqlalchemy.base import UUIDBase


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
