from datetime import datetime
from typing import NamedTuple
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel as _BaseModel

from SimplyTransport.domain.database_statistics.statistic_type import StatisticType


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class DatabaseStatisticModel(BigIntAuditBase):
    __tablename__ = "database_statistic"
    __table_args__ = (Index("ix_statistic_created_at", "created_at"),)

    statistic_type: Mapped[StatisticType] = mapped_column(String(length=255), index=True)
    key: Mapped[str] = mapped_column(String(length=255), index=True)
    value: Mapped[int] = mapped_column(Integer())


class DatabaseStatistic(BaseModel):
    statistic_type: StatisticType
    key: str
    value: int
    created_at: datetime


class DatabaseStatisticWithPercentage(NamedTuple):
    key: str
    value: int
    percentage: float