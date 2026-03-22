"""Batched PostgreSQL Core ``INSERT`` and ``INSERT ... ON CONFLICT DO UPDATE`` helpers."""

from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.sql.dml import Insert

DEFAULT_BULK_INSERT_BATCH_SIZE = 3000

_AsyncSessionish = AsyncSession | async_scoped_session[AsyncSession]


def _bulk_upsert_statement(
    model: type,
    objects_to_commit: list[dict[str, Any]],
    index_elements: list[str],
    update_dict: dict[str, str],
) -> Insert:
    stmt = insert(model).values(objects_to_commit)
    return stmt.on_conflict_do_update(
        index_elements=index_elements,
        set_={key: getattr(stmt.excluded, key) for key in update_dict},
    )


async def bulk_insert(
    session: _AsyncSessionish,
    model: type,
    rows: list[dict[str, Any]],
    *,
    batch_size: int = DEFAULT_BULK_INSERT_BATCH_SIZE,
    auto_commit: bool = True,
) -> None:
    """Insert many rows using ``INSERT ... VALUES (...), (...), ...`` per batch."""
    if not rows:
        return
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        await session.execute(insert(model).values(batch))
    if auto_commit:
        await session.commit()


async def bulk_upsert(
    session: _AsyncSessionish,
    model: type,
    objects_to_commit: list[dict[str, Any]],
    index_elements: list[str],
    update_dict: dict[str, str],
    *,
    batch_size: int = DEFAULT_BULK_INSERT_BATCH_SIZE,
    auto_commit: bool = True,
) -> None:
    """Upsert many rows in batches (``ON CONFLICT DO UPDATE`` on ``index_elements``)."""
    for i in range(0, len(objects_to_commit), batch_size):
        batch = objects_to_commit[i : i + batch_size]
        stmt = _bulk_upsert_statement(model, batch, index_elements, update_dict)
        await session.execute(stmt)
    if auto_commit:
        await session.commit()
