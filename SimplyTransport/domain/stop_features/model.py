from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel
from typing import Optional
from datetime import datetime as dateTime
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..stop.model import StopModel

from ..enums import Bearing, StopType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class StopFeatureModel(BigIntAuditBase):
    __tablename__ = "stop_feature"

    # https://data.gov.ie/dataset/70c5967e-4df7-4dc8-82bb-c7e2b0e00888/resource/46702e02-79ac-456b-a3a9-d6cbd3c04abb/download/ptimsglossary.pdf
    # STOPS
    stop_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("stop.id", ondelete="CASCADE"), index=True
    )
    stop: Mapped["StopModel"] = relationship(back_populates="stop_feature")  # noqa: F821
    stop_name_ie: Mapped[Optional[str]] = mapped_column(String(length=1000))
    stop_type: Mapped[Optional[StopType]] = mapped_column(String(length=20))
    bearing: Mapped[Optional[Bearing]] = mapped_column(String(length=2))
    nptg_locality_ref: Mapped[Optional[str]] = mapped_column(String(length=1000))
    bays: Mapped[Optional[int]] = mapped_column(Integer)
    standing_area: Mapped[Optional[bool]] = mapped_column(Boolean)
    bike_stand: Mapped[Optional[bool]] = mapped_column(Boolean)
    bench: Mapped[Optional[bool]] = mapped_column(Boolean)
    bin: Mapped[Optional[bool]] = mapped_column(Boolean)
    stop_accessability: Mapped[Optional[bool]] = mapped_column(Boolean)
    wheelchair_accessability: Mapped[Optional[bool]] = mapped_column(Boolean)
    castle_kerbing: Mapped[Optional[bool]] = mapped_column(Boolean)
    footpath_to_stop: Mapped[Optional[bool]] = mapped_column(Boolean)
    step_at_stop: Mapped[Optional[bool]] = mapped_column(Boolean)
    bike_lane_front: Mapped[Optional[bool]] = mapped_column(Boolean)
    bike_lane_rear: Mapped[Optional[bool]] = mapped_column(Boolean)
    surveyed: Mapped[Optional[bool]] = mapped_column(Boolean)
    ud_surveyor: Mapped[Optional[str]] = mapped_column(String(length=1000))
    ud_calculated: Mapped[Optional[str]] = mapped_column(String(length=100))
    # RTPI
    rtpi_active: Mapped[bool] = mapped_column(Boolean, default=False)
    lines: Mapped[Optional[str]] = mapped_column(String(length=1000))
    integrated_into_shelter: Mapped[Optional[bool]] = mapped_column(Boolean)
    last_updated_rtpi: Mapped[Optional[dateTime]] = mapped_column(DateTime)
    # SHELTERS
    shelter_active: Mapped[bool] = mapped_column(Boolean, default=False)
    shelter_description: Mapped[Optional[str]] = mapped_column(String(length=1000))
    shelter_type: Mapped[Optional[int]] = mapped_column(Integer)
    power: Mapped[Optional[bool]] = mapped_column(Boolean)
    light: Mapped[Optional[bool]] = mapped_column(Boolean)
    last_updated_shelter: Mapped[Optional[dateTime]] = mapped_column(DateTime)
    # POLES
    pole_active: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[Optional[str]] = mapped_column(String(length=1000))
    pole_type: Mapped[Optional[str]] = mapped_column(String(length=1000))
    socket_type: Mapped[Optional[str]] = mapped_column(String(length=1000))
    last_updated_pole: Mapped[Optional[dateTime]] = mapped_column(DateTime)

    dataset: Mapped[str] = mapped_column(String(length=1000), index=True)

    def pretty_string(self, attr_name):
        value = getattr(self, attr_name, None)
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")  # Modify this to your preferred format
        else:
            return str(value)


class StopFeature(BaseModel):
    stop_id: str
    stop_name_ie: Optional[str]
    stop_type: Optional[StopType]
    bearing: Optional[Bearing]
    nptg_locality_ref: Optional[str]
    bays: Optional[int]
    standing_area: Optional[bool]
    bike_stand: Optional[bool]
    bench: Optional[bool]
    bin: Optional[bool]
    stop_accessability: Optional[bool]
    wheelchair_accessability: Optional[bool]
    castle_kerbing: Optional[bool]
    footpath_to_stop: Optional[bool]
    step_at_stop: Optional[bool]
    bike_lane_front: Optional[bool]
    bike_lane_rear: Optional[bool]
    surveyed: Optional[bool]
    ud_surveyor: Optional[str]
    ud_calculated: Optional[str]
    rtpi_active: Optional[bool]
    lines: Optional[str]
    integrated_into_shelter: Optional[bool]
    last_updated_rtpi: Optional[dateTime]
    shelter_active: Optional[bool]
    shelter_description: Optional[str]
    shelter_type: Optional[int]
    power: Optional[bool]
    light: Optional[bool]
    last_updated_shelter: Optional[dateTime]
    pole_active: Optional[bool]
    position: Optional[str]
    pole_type: Optional[str]
    socket_type: Optional[str]
    last_updated_pole: Optional[dateTime]
    dataset: str
