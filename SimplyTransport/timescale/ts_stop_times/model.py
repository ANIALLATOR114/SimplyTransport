from datetime import datetime, time
from litestar.contrib.sqlalchemy.base import BigIntBase

from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel, Field, computed_field


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class TS_StopTimeModel(BigIntBase):
    __tablename__ = "ts_stop_times"

    Timestamp: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, primary_key=True
    )
    stop_id: Mapped[str] = mapped_column(String(length=1000), nullable=False, index=True)
    route_code: Mapped[str] = mapped_column(String(length=1000), nullable=False, index=True)
    scheduled_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    delay_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class TS_StopTime(BaseModel):
    Timestamp: datetime
    stop_id: str
    route_code: str
    scheduled_time: time
    delay_in_seconds: int

    @computed_field
    @property
    def delay_in_minutes(self) -> float:
        return round(self.delay_in_seconds / 60, 1)


class TS_StopTimeForGraph(BaseModel):
    Timestamp: datetime
    delay_in_seconds: int = Field(exclude=True)

    @computed_field
    @property
    def delay_in_minutes(self) -> float:
        return round(self.delay_in_seconds / 60, 1)


class TS_StopTimeDelayAggregated(BaseModel):
    avg: int
    max: int
    min: int
    standard_deviation: float
    p50: int
    p75: int
    p90: int
    samples: int
