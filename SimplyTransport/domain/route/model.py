from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel, Field
from enum import Enum
from typing import Optional


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RouteType(int, Enum):
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLYBUS = 11
    MONORAIL = 12


class RouteModel(BigIntAuditBase):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    agency_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("agency.id", ondelete="CASCADE")
    )
    agency: Mapped["AgencyModel"] = relationship(back_populates="routes")  # noqa: F821
    short_name: Mapped[str] = mapped_column(String(length=1000))
    long_name: Mapped[str] = mapped_column(String(length=1000))
    description: Mapped[Optional[str]] = mapped_column(String(length=1000))
    route_type: Mapped[RouteType] = mapped_column(Integer)
    url: Mapped[Optional[str]] = mapped_column(String(length=1000))
    color: Mapped[Optional[str]] = mapped_column(String(length=1000))
    text_color: Mapped[Optional[str]] = mapped_column(String(length=1000))
    trips: Mapped[list["TripModel"]] = relationship(back_populates="route")   # noqa: F821
    dataset: Mapped[str] = mapped_column(String(length=80))


class Route(BaseModel):
    id: str
    agency_id: str
    short_name: str
    long_name: str
    description: Optional[str]
    route_type: RouteType = Field(
        description="Indicates the type of transportation used on a route",
    )
    url: Optional[str]
    color: Optional[str]
    text_color: Optional[str]
    dataset: str


class RouteWithTotal(BaseModel):
    total: int
    routes: list[Route]
