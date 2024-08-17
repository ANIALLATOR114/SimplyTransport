import asyncio
from logging.config import fileConfig

from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from SimplyTransport.lib import settings


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = UUIDBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Retreives the DB name from the cmd args
cmd_kwargs = context.get_x_argument(as_dictionary=True)
if 'db' not in cmd_kwargs:
    raise Exception('We couldn\'t find `db` in the CLI arguments. '
                    'Please verify `alembic` was run with `-x db=<db_name>` '
                    '(e.g. `alembic -x db=main upgrade head`)')
db_name = cmd_kwargs['db']

# Ensure correct domain is in scope for the migration
if db_name == "main":
    from SimplyTransport import domain  # noqa: F401
    target_metadata = UUIDBase.metadata
elif db_name == "timescale":
    from SimplyTransport import timescale  # noqa: F401


def get_database_url() -> str:
    """Retrieve the appropriate database URL based on the Alembic configuration."""
    if db_name == "main":
        return settings.app.DB_URL
    elif db_name == "timescale":
        return settings.app.TIMESCALE_URL
    else:
        raise ValueError(f"Unknown database name: {db_name}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
