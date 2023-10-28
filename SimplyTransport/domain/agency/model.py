from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel
from typing import Optional


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class AgencyModel(BigIntAuditBase):
    __tablename__ = "agency"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=1000))
    url: Mapped[str] = mapped_column(String(length=1000))
    timezone: Mapped[str] = mapped_column(String(length=1000))
    dataset: Mapped[str] = mapped_column(String(length=80))
    routes: Mapped[list["RouteModel"]] = relationship(
        back_populates="agency", cascade="all, delete"
    )


class Agency(BaseModel):
    id: str
    name: str
    url: str
    timezone: str
    dataset: str
    # routes...


class AgencyWithTotal(BaseModel):
    total: int
    agencies: list[Agency]
