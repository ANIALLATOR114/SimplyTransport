from datetime import date as datetype
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..calendar.model import CalendarModel

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..enums import ExceptionType

__all__ = ["CalendarDateModel"]


class CalendarDateModel(BigIntAuditBase):
    __tablename__: str = "calendar_date"  # type: ignore[assignment]

    service_id: Mapped[str] = mapped_column(
        String(length=1000), ForeignKey("calendar.id", ondelete="CASCADE"), index=True
    )
    service: Mapped["CalendarModel"] = relationship(back_populates="calendar_dates")
    date: Mapped[datetype] = mapped_column(Date)
    exception_type: Mapped[ExceptionType] = mapped_column("exception_type", String(length=20))
    dataset: Mapped[str] = mapped_column(String(length=80))
