from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel, Field
from datetime import date
from enum import Enum


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class ExceptionType(str, Enum):
    added = "added"
    removed = "removed"


class CalendarDateModel(BigIntAuditBase):
    __tablename__ = "calendar_date"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("calendar.id", ondelete="CASCADE"))
    service: Mapped["CalendarModel"] = relationship(back_populates="calendar_dates")
    date: Mapped[date] = mapped_column(Date)
    exception_type: Mapped[ExceptionType] = mapped_column("exception_type", String(length=20))
    dataset: Mapped[str] = mapped_column(String(length=80))


class CalendarDate(BaseModel):
    id: int
    service_id: str
    date: date
    exception_type: ExceptionType = Field(
        description="Determines whether the service is added or removed on the date",
        examples=["added", "removed"],
    )
    dataset: str


class CalendarDateWithTotal(BaseModel):
    total: int
    calendar_dates: list[CalendarDate]
