from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import ScheduleRealtionship

if TYPE_CHECKING:
    from SimplyTransport.domain.stop.model import StopModel
    from SimplyTransport.domain.trip.model import TripModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTStopTimeModel(BigIntAuditBase):
    __tablename__ = "rt_stop_time"  # type: ignore
    __table_args__ = (
        Index("ix_rt_stop_time_created_at", "created_at"),
        UniqueConstraint(
            "stop_id", "trip_id", "stop_sequence", "dataset"
        ),  # Only store the most recent update per stop_sequence for each trip
    )

    stop: Mapped["StopModel"] = relationship(back_populates="rt_stop_times")
    stop_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("stop.id", ondelete="CASCADE"), index=True
    )
    trip: Mapped["TripModel"] = relationship(back_populates="rt_stop_times")
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True
    )
    stop_sequence: Mapped[int] = mapped_column(Integer)
    schedule_relationship: Mapped[ScheduleRealtionship] = mapped_column(String(length=1000))
    arrival_delay: Mapped[int | None] = mapped_column(Integer)
    departure_delay: Mapped[int | None] = mapped_column(Integer)
    entity_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    dataset: Mapped[str] = mapped_column(String(length=80))
    # If you add a new field, remember to update the batch insert query in the realtime importer


class RTStopTime(BaseModel):
    stop_id: str
    trip_id: str
    stop_sequence: int
    schedule_relationship: ScheduleRealtionship
    arrival_delay: int
    departure_delay: int
