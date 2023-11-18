from datetime import date, time

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from pydantic import Field
from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from SimplyTransport.domain.realtime.enums import ScheduleRealtionship
from SimplyTransport.domain.trip.model import Direction


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTTripModel(BigIntAuditBase):
    __tablename__ = "rt_trip"

    trip: Mapped["TripModel"] = relationship(back_populates="rt_trips")  # noqa: F821
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id"), index=True
    )
    route: Mapped["RouteModel"] = relationship(back_populates="rt_trips")  # noqa: F821
    route_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("route.id"), index=True
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
    direction: Direction = Field(
        description="Direction of travel. Mapping between agencies could differ."
    )

