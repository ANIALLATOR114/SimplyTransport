from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel
from typing import Optional
from datetime import date


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class CalendarModel(BigIntAuditBase):
    __tablename__ = "calendar"

    id: Mapped[str] = mapped_column("id", String(length=1000), primary_key=True)
    monday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    tuesday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    wednesday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    thursday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    friday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    saturday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    sunday: Mapped[Optional[str]] = mapped_column(String(length=1000))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    # trips...


class Calendar(BaseModel):
    id: str
    monday: Optional[str]
    tuesday: Optional[str]
    wednesday: Optional[str]
    thursday: Optional[str]
    friday: Optional[str]
    saturday: Optional[str]
    sunday: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    # trips...
