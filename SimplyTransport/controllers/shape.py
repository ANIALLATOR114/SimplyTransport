from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.shape.model import Shape
from SimplyTransport.domain.shape.repo import ShapeRepository, provide_shape_repo
from litestar.params import Parameter
from advanced_alchemy.filters import OrderBy

__all__ = ["shapeController"]


class ShapeController(Controller):
    dependencies = {"repo": Provide(provide_shape_repo)}

    @get("/{id:int}", summary="Shape by ID", raises=[NotFoundException])
    async def get_shape_by_id(self, repo: ShapeRepository, id: int) -> Shape:
        try:
            result = await repo.get(id)
        except NotFoundError:
            raise NotFoundException(detail=f"Shape not found with id {id}")
        return Shape.model_validate(result)
    
    @get("/shapes/{shape_id:str}", summary="List of Shapes by shape Id", raises=[NotFoundException])
    async def get_shape_by_shape_id(self, repo: ShapeRepository, shape_id: str, order_by_shape:OrderBy) -> list[Shape]:
        try:
            result = await repo.list(order_by_shape,shape_id=shape_id)
        except NotFoundError:
            raise NotFoundException(detail=f"Shapes not found with id {shape_id}")
        return [Shape.model_validate(obj) for obj in result]
    