from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["ShapeModel"]


class ShapeModel(BigIntAuditBase):
    __tablename__ = "shape"  # type: ignore
    shape_id: Mapped[str] = mapped_column(String(length=1000), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    sequence: Mapped[int] = mapped_column(Integer)
    distance: Mapped[float | None] = mapped_column(Float)
    dataset: Mapped[str] = mapped_column(String(length=80))
