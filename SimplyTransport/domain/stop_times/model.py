import datetime as DateTime
from datetime import time
from typing import Optional

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from SimplyTransport.domain.enums import PickupType, DropoffType, Timepoint

class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class StopTimeModel(BigIntAuditBase):
    __tablename__ = "stop_time"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True
    )
    trip: Mapped["TripModel"] = relationship(back_populates="stop_times")  # noqa: F821
    arrival_time: Mapped[time] = mapped_column(Time)
    departure_time: Mapped[time] = mapped_column(Time)
    stop_id: Mapped[str] = mapped_column(ForeignKey("stop.id"), index=True)
    stop: Mapped["StopModel"] = relationship(back_populates="stop_times")  # noqa: F821
    stop_sequence: Mapped[int] = mapped_column(Integer)
    stop_headsign: Mapped[Optional[str]] = mapped_column(String(length=1000))
    pickup_type: Mapped[Optional[PickupType]] = mapped_column(Integer)
    dropoff_type: Mapped[Optional[DropoffType]] = mapped_column(Integer)
    timepoint: Mapped[Optional[Timepoint]] = mapped_column(Integer)
    dataset: Mapped[str] = mapped_column(String(length=80))

    def true_if_active_between_times(self, start_time: DateTime.time, end_time: DateTime.time):
        """Returns True if the stop time arrival_time is active between the two times"""
        if start_time <= self.arrival_time <= end_time:
            return True


class StopTime(BaseModel):
    id: int
    trip_id: str
    arrival_time: time
    departure_time: time
    stop_id: str
    stop_sequence: int
    stop_headsign: Optional[str]
    pickup_type: Optional[PickupType]
    dropoff_type: Optional[DropoffType]
    timepoint: Optional[Timepoint]
    dataset: str
