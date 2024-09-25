from datetime import datetime, time
from litestar.contrib.sqlalchemy.base import BigIntBase

from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class TS_StopTimeModel(BigIntBase):
    __tablename__ = "ts_stop_times"

    Timestamp: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, primary_key=True
    )
    stop_id: Mapped[str] = mapped_column(
        String(length=1000), nullable=False, index=True
    )
    route_code: Mapped[str] = mapped_column(String(length=1000), nullable=False, index=True)
    scheduled_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    delay_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class TS_StopTime(BaseModel):
    Timestamp: datetime
    stop_id: str
    route_code: str
    scheduled_time: time
    delay_in_seconds: int
