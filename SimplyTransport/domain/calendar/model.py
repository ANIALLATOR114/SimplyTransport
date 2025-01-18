from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..trip.model import TripModel

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..calendar_dates.model import CalendarDateModel


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class CalendarModel(BigIntAuditBase):
    __tablename__: str = "calendar"  # type: ignore[assignment]

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
    calendar_dates: Mapped[list["CalendarDateModel"]] = relationship(
        back_populates="service", cascade="all, delete"
    )
    trips: Mapped[list["TripModel"]] = relationship(back_populates="service")

    def true_if_active(self, date: date):
        """Returns True if the calendar is active on the given date"""
        if self.start_date <= date <= self.end_date:
            return True
        return False

    def in_exceptions(self, exceptions: list[CalendarDateModel]):
        """This assumes that the exceptions passed are active on the given date"""
        for exception in exceptions:
            if exception.service_id == self.id:
                return True
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
