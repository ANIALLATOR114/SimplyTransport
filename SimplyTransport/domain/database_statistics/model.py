from typing import NamedTuple

from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from SimplyTransport.domain.database_statistics.statistic_type import StatisticType

__all__ = ["DatabaseStatisticModel", "DatabaseStatisticWithPercentage"]


class DatabaseStatisticModel(BigIntAuditBase):
    __tablename__: str = "database_statistic"  # type: ignore[assignment]

    __table_args__ = (Index("ix_statistic_created_at", "created_at"),)

    statistic_type: Mapped[StatisticType] = mapped_column(String(length=255), index=True)
    key: Mapped[str] = mapped_column(String(length=255), index=True)
    value: Mapped[int] = mapped_column(Integer())


class DatabaseStatisticWithPercentage(NamedTuple):
    key: str
    value: int
    percentage: float
