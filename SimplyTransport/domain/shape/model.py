from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from pydantic import BaseModel as _BaseModel
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class ShapeModel(BigIntAuditBase):
    __tablename__ = "shape"
    shape_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    sequence: Mapped[int] = mapped_column(Integer)
    distance: Mapped[float | None] = mapped_column(Float)
    dataset: Mapped[str] = mapped_column(String(length=80))


class Shape(BaseModel):
    id: int
    shape_id: str
    lat: float
    lon: float
    sequence: int
    distance: float | None
    dataset: str
