from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel, Field
from typing import Optional

from SimplyTransport.domain.enums import LocationType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class StopModel(BigIntAuditBase):
    __tablename__ = "stop"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(String(length=1000), index=True)
    name: Mapped[str] = mapped_column(String(length=1000), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(length=1000))
    lat: Mapped[Optional[float]] = mapped_column(Float)
    lon: Mapped[Optional[float]] = mapped_column(Float)
    zone_id: Mapped[Optional[str]] = mapped_column(String(length=1000))
    url: Mapped[Optional[str]] = mapped_column(String(length=1000))
    location_type: Mapped[Optional[LocationType]] = mapped_column(Integer)
    parent_station: Mapped[Optional[str]] = mapped_column(
        String(length=1000), ForeignKey("stop.id")
    )
    stop_times: Mapped[list["StopTimeModel"]] = relationship(  # noqa: F821
        back_populates="stop",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    rt_stop_times: Mapped[list["RTStopTimeModel"]] = relationship(
        back_populates="stop"
    )  # noqa: F821
    dataset: Mapped[str] = mapped_column(String(length=80))


class Stop(BaseModel):
    id: str
    code: Optional[str]
    name: str
    description: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    zone_id: Optional[str]
    url: Optional[str]
    location_type: Optional[LocationType] = Field(
        description="Indicates the type of the location",
    )
    parent_station: Optional[str]
    dataset: str
