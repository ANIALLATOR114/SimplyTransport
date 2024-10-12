from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel as _BaseModel, Field
from datetime import date as dateType

from ..enums import ExceptionType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class CalendarDateModel(BigIntAuditBase):
    __tablename__ = "calendar_date"

    service_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("calendar.id", ondelete="CASCADE"), index=True
    )
    service: Mapped["CalendarModel"] = relationship(back_populates="calendar_dates")  # noqa: F821
    date: Mapped[dateType] = mapped_column(Date)
    exception_type: Mapped[ExceptionType] = mapped_column("exception_type", String(length=20))
    dataset: Mapped[str] = mapped_column(String(length=80))


class CalendarDate(BaseModel):
    id: int
    service_id: str
    date: dateType
    exception_type: ExceptionType = Field(
        description="Determines whether the service is added or removed on the date",
        examples=["added", "removed"],
    )
    dataset: str


class CalendarDateWithTotal(BaseModel):
    total: int
    calendar_dates: list[CalendarDate]
