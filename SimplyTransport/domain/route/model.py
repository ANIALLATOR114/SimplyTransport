from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import RouteType

if TYPE_CHECKING:
    from SimplyTransport.domain.agency.model import AgencyModel
    from SimplyTransport.domain.realtime.trip.model import RTTripModel
    from SimplyTransport.domain.trip.model import TripModel

__all__ = ["RouteModel"]


class RouteModel(BigIntAuditBase):
    __tablename__ = "route"  # type: ignore

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    agency_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("agency.id", ondelete="CASCADE"), index=True
    )
    agency: Mapped["AgencyModel"] = relationship(back_populates="routes")
    short_name: Mapped[str] = mapped_column(String(length=1000), index=True)
    long_name: Mapped[str] = mapped_column(String(length=1000), index=True)
    description: Mapped[str | None] = mapped_column(String(length=1000))
    route_type: Mapped[RouteType] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String(length=1000))
    color: Mapped[str | None] = mapped_column(String(length=1000))
    text_color: Mapped[str | None] = mapped_column(String(length=1000))
    trips: Mapped[list["TripModel"]] = relationship(back_populates="route")
    rt_trips: Mapped[list["RTTripModel"]] = relationship(back_populates="route")
    dataset: Mapped[str] = mapped_column(String(length=80), index=True)
