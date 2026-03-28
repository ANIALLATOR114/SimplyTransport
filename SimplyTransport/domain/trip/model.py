from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import Direction

if TYPE_CHECKING:
    from SimplyTransport.domain.calendar.model import CalendarModel
    from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
    from SimplyTransport.domain.realtime.trip.model import RTTripModel
    from SimplyTransport.domain.realtime.vehicle.model import RTVehicleModel
    from SimplyTransport.domain.route.model import RouteModel
    from SimplyTransport.domain.stop_times.model import StopTimeModel

__all__ = ["Direction", "TripModel"]


class TripModel(BigIntAuditBase):
    __tablename__ = "trip"  # type: ignore

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    route: Mapped["RouteModel"] = relationship(back_populates="trips")
    route_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("route.id", ondelete="CASCADE"), index=True
    )
    service_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("calendar.id", ondelete="CASCADE"), index=True
    )
    service: Mapped["CalendarModel"] = relationship(back_populates="trips")
    stop_times: Mapped[list["StopTimeModel"]] = relationship(back_populates="trip")
    headsign: Mapped[str | None] = mapped_column(String(length=1000))
    short_name: Mapped[str | None] = mapped_column(String(length=1000))
    direction: Mapped[Direction] = mapped_column(Integer)
    block_id: Mapped[str | None] = mapped_column(String(length=1000))
    shape_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    rt_trips: Mapped[list["RTTripModel"]] = relationship(back_populates="trip")
    rt_stop_times: Mapped[list["RTStopTimeModel"]] = relationship(back_populates="trip")
    rt_vehicles: Mapped[list["RTVehicleModel"]] = relationship(back_populates="trip")
    dataset: Mapped[str] = mapped_column(String(length=80), index=True)
