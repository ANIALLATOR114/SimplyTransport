from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel, Field
from enum import Enum
from typing import Optional


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class Direction(int, Enum):
    """Direction of travel"""

    OUTBOUND = 0
    INBOUND = 1


class TripModel(BigIntAuditBase):
    __tablename__ = "trip"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    route: Mapped["RouteModel"] = relationship(back_populates="trips")
    route_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("route.id", ondelete="CASCADE")
    )
    service_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("calendar.id", ondelete="CASCADE")
    )
    service: Mapped["CalendarModel"] = relationship(back_populates="trips")
    stop_times: Mapped[list["StopTimeModel"]] = relationship(back_populates="trip")
    headsign: Mapped[Optional[str]] = mapped_column(String(length=1000))
    short_name: Mapped[Optional[str]] = mapped_column(String(length=1000))
    direction: Mapped[Direction] = mapped_column(Integer)
    block_id: Mapped[Optional[str]] = mapped_column(String(length=1000))
    shape_id: Mapped[str] = mapped_column(String(length=1000))
    dataset: Mapped[str] = mapped_column(String(length=80))


class Trip(BaseModel):
    id: str
    route_id: str
    service_id: str
    shape_id: str
    headsign: Optional[str]
    short_name: Optional[str]
    direction: Direction = Field(
        description="Direction of travel. Mapping between agencies could differ."
    )
    block_id: Optional[str]
    dataset: str


class TripsWithTotal(BaseModel):
    total: int
    trips: list[Trip]
