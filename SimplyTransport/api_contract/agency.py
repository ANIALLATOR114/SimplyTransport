from SimplyTransport.api_contract.base import ApiBaseModel


class Agency(ApiBaseModel):
    id: str
    name: str
    url: str
    timezone: str
    dataset: str


class AgencyWithTotal(ApiBaseModel):
    total: int
    agencies: list[Agency]
