from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from pydantic import Field
from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import LocationType

if TYPE_CHECKING:
    from ..realtime.stop_time.model import RTStopTimeModel
    from ..stop_features.model import StopFeatureModel
    from ..stop_times.model import StopTimeModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class StopModel(BigIntAuditBase):
    __tablename__: str = "stop"  # type: ignore[assignment]
    __table_args__ = (Index("idx_stop_coordinates", "lat", "lon"),)

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    code: Mapped[str | None] = mapped_column(String(length=1000), index=True)
    name: Mapped[str] = mapped_column(String(length=1000), index=True)
    description: Mapped[str | None] = mapped_column(String(length=1000))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    zone_id: Mapped[str | None] = mapped_column(String(length=1000))
    url: Mapped[str | None] = mapped_column(String(length=1000))
    location_type: Mapped[LocationType | None] = mapped_column(Integer)
    parent_station: Mapped[str | None] = mapped_column(String(length=1000), ForeignKey("stop.id"))
    stop_times: Mapped[list["StopTimeModel"]] = relationship(
        back_populates="stop",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    rt_stop_times: Mapped[list["RTStopTimeModel"]] = relationship(back_populates="stop")
    stop_feature: Mapped["StopFeatureModel"] = relationship(back_populates="stop")
    dataset: Mapped[str] = mapped_column(String(length=80))


class Stop(BaseModel):
    id: str
    code: str | None
    name: str
    description: str | None
    lat: float | None
    lon: float | None
    zone_id: str | None
    url: str | None
    location_type: LocationType | None = Field(
        description="Indicates the type of the location",
    )
    parent_station: str | None
    dataset: str
