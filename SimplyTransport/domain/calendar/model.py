from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel
from datetime import date


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class CalendarModel(BigIntAuditBase):
    __tablename__ = "calendar"

    id: Mapped[str] = mapped_column("id", String(length=1000), primary_key=True)
    monday: Mapped[int] = mapped_column(Integer)
    tuesday: Mapped[int] = mapped_column(Integer)
    wednesday: Mapped[int] = mapped_column(Integer)
    thursday: Mapped[int] = mapped_column(Integer)
    friday: Mapped[int] = mapped_column(Integer)
    saturday: Mapped[int] = mapped_column(Integer)
    sunday: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    dataset: Mapped[str] = mapped_column("dataset", String(length=80))
    # trips...


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
    # trips...


class CalendarWithTotal(BaseModel):
    total: int
    calendars: list[Calendar]
