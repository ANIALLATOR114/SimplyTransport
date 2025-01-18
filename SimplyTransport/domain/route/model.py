from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from pydantic import Field
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import RouteType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RouteModel(BigIntAuditBase):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    agency_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("agency.id", ondelete="CASCADE"), index=True
    )
    agency: Mapped["AgencyModel"] = relationship(back_populates="routes")  # noqa: F821
    short_name: Mapped[str] = mapped_column(String(length=1000), index=True)
    long_name: Mapped[str] = mapped_column(String(length=1000), index=True)
    description: Mapped[str | None] = mapped_column(String(length=1000))
    route_type: Mapped[RouteType] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String(length=1000))
    color: Mapped[str | None] = mapped_column(String(length=1000))
    text_color: Mapped[str | None] = mapped_column(String(length=1000))
    trips: Mapped[list["TripModel"]] = relationship(back_populates="route")  # noqa: F821
    rt_trips: Mapped[list["RTTripModel"]] = relationship(back_populates="route")  # noqa: F821
    dataset: Mapped[str] = mapped_column(String(length=80))


class Route(BaseModel):
    id: str
    agency_id: str
    short_name: str
    long_name: str
    description: str | None
    route_type: RouteType = Field(
        description="Indicates the type of transportation used on a route",
    )
    url: str | None
    color: str | None
    text_color: str | None
    dataset: str


class RouteWithTotal(BaseModel):
    total: int
    routes: list[Route]
