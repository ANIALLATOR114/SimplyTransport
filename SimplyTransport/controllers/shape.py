from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from SimplyTransport.domain.shape.model import Shape
from SimplyTransport.domain.shape.repo import ShapeRepository, provide_shape_repo
from advanced_alchemy.filters import OrderBy

__all__ = ["shapeController"]


class ShapeController(Controller):
    dependencies = {"repo": Provide(provide_shape_repo)}

    @get("/{shape_id:str}", summary="List of Shapes by shape Id", raises=[NotFoundException])
    async def get_shape_by_shape_id(
        self, repo: ShapeRepository, shape_id: str, order_by_shape: OrderBy
    ) -> list[Shape]:
        result = await repo.list(order_by_shape, shape_id=shape_id)
        if not result or len(result) == 0:
            raise NotFoundException(detail=f"Shapes not found with id {shape_id}")
        return [Shape.model_validate(obj) for obj in result]
