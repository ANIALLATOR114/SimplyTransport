from datetime import datetime
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RTVehicleModel(BigIntAuditBase):
    __tablename__ = "rt_vehicle"

    vehicle_id: Mapped[int] = mapped_column(Integer)
    trip: Mapped["TripModel"] = relationship(back_populates="rt_vehicles")  # noqa: F821
    trip_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("trip.id", ondelete="CASCADE"), index=True
    )
    time_of_update: Mapped[datetime] = mapped_column(DateTime)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    dataset: Mapped[str] = mapped_column(String(length=80))


class RTVehicle(BaseModel):
    vehicle_id: int
    trip_id: str
    time_of_update: datetime
    lat: float
    lon: float
    dataset: str
