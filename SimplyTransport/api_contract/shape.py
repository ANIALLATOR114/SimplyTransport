from SimplyTransport.api_contract.base import ApiBaseModel


class Shape(ApiBaseModel):
    id: int
    shape_id: str
    lat: float
    lon: float
    sequence: int
    distance: float | None
    dataset: str
