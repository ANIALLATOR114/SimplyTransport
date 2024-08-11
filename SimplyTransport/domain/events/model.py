from datetime import date, datetime, timedelta
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import DateTime, Index, String
from typing import Any
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel
import json

from .event_types import EventType
from ...lib.time_date_conversions import DateTimeEncoderForJson


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class EventModel(BigIntAuditBase):
    __tablename__ = "event"
    __table_args__ = (Index("ix_event_created_at", "created_at"),)

    event_type: Mapped[EventType] = mapped_column(String(length=255), index=True)
    description: Mapped[str] = mapped_column(String(length=1000))
    expiry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attributes: Mapped[dict] = mapped_column(JSONB)

    def to_dict(self) -> dict[str, Any]:
        exclude = {"updated_at"}
        return super().to_dict(exclude)

    def to_json(self, indent: int = 4) -> str:
        return json.dumps(self.to_dict(), cls=DateTimeEncoderForJson, indent=indent)

    def add_pretty_created_at(self):
        """Adds a created_at_pretty to an event"""
        now = datetime.now()
        if self.created_at.date() == now.date():
            self.created_at_pretty = "Today - " + self.created_at.strftime("%H:%M")
        elif self.created_at.date() == (now - timedelta(days=1)).date():
            self.created_at_pretty = "Yesterday - " + self.created_at.strftime("%H:%M")
        else:
            self.created_at_pretty = self.created_at.strftime("%d %b - %H:%M")
        return self


class Event(BaseModel):
    id: int
    event_type: EventType
    description: str
    expiry_time: datetime
    attributes: dict
    created_at : datetime


class EventsWithTotal(BaseModel):
    total: int
    events: list[Event]
