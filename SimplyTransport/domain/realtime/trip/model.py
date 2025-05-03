from datetime import date, time
from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from pydantic import Field
from sqlalchemy import Date, ForeignKey, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from ...route.model import RouteModel
    from ...trip.model import TripModel

from ...trip.model import Direction
from ..enums import ScheduleRealtionship


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTTripModel(BigIntAuditBase):
    __tablename__ = "rt_trip"  # type: ignore
    __table_args__ = (
        Index("ix_rt_trip_created_at", "created_at"),
        UniqueConstraint(
            "trip_id", "route_id", "dataset"
        ),  # Only store the most recent update per trip for each route
    )

    trip: Mapped["TripModel"] = relationship(back_populates="rt_trips")
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True
    )
    route: Mapped["RouteModel"] = relationship(back_populates="rt_trips")
    route_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("route.id", ondelete="CASCADE"), index=True
    )
    start_time: Mapped[time] = mapped_column(Time)
    start_date: Mapped[date] = mapped_column(Date)
    schedule_relationship: Mapped[ScheduleRealtionship] = mapped_column(String(length=1000))
    direction: Mapped[Direction] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    dataset: Mapped[str] = mapped_column(String(length=80))


class RTTrip(BaseModel):
    trip_id: str
    route_id: str
    start_time: time
    start_date: date
    schedule_relationship: ScheduleRealtionship
    direction: Direction = Field(description="Direction of travel. Mapping between agencies could differ.")
