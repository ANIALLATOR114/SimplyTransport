from pydantic import Field

from SimplyTransport.api_contract.base import ApiBaseModel
from SimplyTransport.domain.enums import LocationType


class Stop(ApiBaseModel):
    id: str
    code: str | None
    name: str
    description: str | None
    lat: float | None
    lon: float | None
    zone_id: str | None
    url: str | None
    location_type: LocationType | None = Field(
        description="Indicates the type of the location",
    )
    parent_station: str | None
    dataset: str
