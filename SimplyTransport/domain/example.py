from litestar.contrib.sqlalchemy.base import UUIDAuditBase, BigIntAuditBase
from sqlalchemy.orm import Mapped, mapped_column
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class ExampleModel(BigIntAuditBase):
    __tablename__ = "examples"
    # length 255
    name: Mapped[str] = mapped_column("name", nullable=False)


class Example(BaseModel):
    name: str


class ExampleRepository(SQLAlchemyAsyncRepository[ExampleModel]):
    """Example repository."""

    model_type = ExampleModel


async def provide_example_repo(db_session: AsyncSession) -> ExampleRepository:
    """This provides the default Example repository."""
    return ExampleRepository(session=db_session)
