from datetime import datetime
from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from SimplyTransport.domain.trip.model import TripModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTVehicleModel(BigIntAuditBase):
    __tablename__ = "rt_vehicle"  # type: ignore

    vehicle_id: Mapped[int] = mapped_column(Integer)
    trip: Mapped["TripModel"] = relationship(back_populates="rt_vehicles")
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True
    )
    time_of_update: Mapped[datetime] = mapped_column(DateTime)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    dataset: Mapped[str] = mapped_column(String(length=80))

    def mins_ago_updated(self) -> str:
        """Returns the number of minutes ago the vehicle was updated."""
        mins = (datetime.now() - self.time_of_update).seconds // 60
        if mins == 0:
            return "Less than a minute ago"
        if mins == 1:
            return "1 min ago"
        return f"{mins} mins ago"


class RTVehicle(BaseModel):
    vehicle_id: int
    trip_id: str
    time_of_update: datetime
    lat: float
    lon: float
    dataset: str
