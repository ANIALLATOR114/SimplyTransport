from datetime import datetime

from SimplyTransport.api_contract.base import ApiBaseModel
from SimplyTransport.domain.database_statistics.statistic_type import StatisticType


class DatabaseStatistic(ApiBaseModel):
    statistic_type: StatisticType
    key: str
    value: int
    created_at: datetime
