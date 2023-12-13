from datetime import date, datetime
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import DateTime, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel

from .event_types import EventType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class EventModel(BigIntAuditBase):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[EventType] = mapped_column(String(length=255), index=True)
    description: Mapped[str] = mapped_column(String(length=1000))
    expiry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attributes: Mapped[dict] = mapped_column(JSONB)


class Event(BaseModel):
    id: int
    event_type: EventType
    description: str
    expiry_time: date
    attributes: dict
