from datetime import datetime
from litestar.contrib.sqlalchemy.base import BigIntBase

from sqlalchemy import DateTime
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
    # Something with stoptimes and trips etc
    # Maybe some offsets from expected times


class TS_StopTime(BaseModel):
    Timestamp: datetime
