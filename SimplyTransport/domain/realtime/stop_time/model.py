from typing import Optional

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from SimplyTransport.domain.realtime.enums import ScheduleRealtionship


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTStopTimeModel(BigIntAuditBase):
    __tablename__ = "rt_stop_time"

    stop: Mapped["StopModel"] = relationship(back_populates="rt_stop_times")  # noqa: F821
    stop_id: Mapped[str] = mapped_column(String(length=1000), ForeignKey("stop.id", ondelete="CASCADE"), index=True)
    trip: Mapped["TripModel"] = relationship(back_populates="rt_stop_times")  # noqa: F821
    trip_id: Mapped[str] = mapped_column(String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True)
    stop_sequence: Mapped[int] = mapped_column(Integer)
    schedule_relationship: Mapped[ScheduleRealtionship] = mapped_column(String(length=1000))
    arrival_delay: Mapped[Optional[int]] = mapped_column(Integer)
    departure_delay: Mapped[Optional[int]] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    dataset: Mapped[str] = mapped_column(String(length=80))


class RTStopTime(BaseModel):
    stop_id: str
    trip_id: str
    stop_sequence: int
    schedule_relationship: ScheduleRealtionship
    arrival_delay: int
    departure_delay: int
