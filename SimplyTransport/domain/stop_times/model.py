from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Integer, ForeignKey, Time
from datetime import time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel
from typing import Optional
from enum import Enum


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class PickupType(int, Enum):
    """Indicates pickup method"""

    REGULARLY_SCHEDULED = 0
    NO_PICKUP = 1
    MUST_PHONE_AGENCY = 2
    MUST_COORDINATE_WITH_DRIVER = 3


class DropoffType(int, Enum):
    """Indicates dropoff method"""

    REGULARLY_SCHEDULED = 0
    NO_DROP_OFF = 1
    MUST_PHONE_AGENCY = 2
    MUST_COORDINATE_WITH_DRIVER = 3


class Timepoint(int, Enum):
    """Indicates if arrival and departure times for a stop are strictly adhered to by the vehicle or if they are instead approximate and/or interpolated times
    A null value here means EXACT
    """

    APPROXIMATE = 0
    EXACT = 1


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
