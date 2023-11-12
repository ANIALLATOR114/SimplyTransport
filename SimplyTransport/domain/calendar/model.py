from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel
from datetime import date

import datetime as DateTime
from SimplyTransport.domain.calendar_dates.model import CalendarDateModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class CalendarModel(BigIntAuditBase):
    __tablename__ = "calendar"

    id: Mapped[str] = mapped_column(String(length=1000), primary_key=True)
    monday: Mapped[int] = mapped_column(Integer)
    tuesday: Mapped[int] = mapped_column(Integer)
    wednesday: Mapped[int] = mapped_column(Integer)
    thursday: Mapped[int] = mapped_column(Integer)
    friday: Mapped[int] = mapped_column(Integer)
    saturday: Mapped[int] = mapped_column(Integer)
    sunday: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    dataset: Mapped[str] = mapped_column(String(length=80))
    calendar_dates: Mapped[list["CalendarDateModel"]] = relationship(  # noqa: F821
        back_populates="service", cascade="all, delete"
    )
    trips: Mapped[list["TripModel"]] = relationship(back_populates="service")  # noqa: F821

    def true_if_active(self, date: DateTime.date):
        """Returns True if the calendar is active on the given date"""
        if self.start_date <= date <= self.end_date:
            return True
        return False

    def not_in_exceptions(self, exceptions: list[CalendarDateModel]):
        """This assumes that the exceptions passed are active on the given date"""
        for exception in exceptions:
            if (
                exception.date == self.start_date
                and exception.exception_type == exception.exception_type.removed
            ):
                return False


class Calendar(BaseModel):
    id: str
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    start_date: date
    end_date: date
    dataset: str


class CalendarWithTotal(BaseModel):
    total: int
    calendars: list[Calendar]
