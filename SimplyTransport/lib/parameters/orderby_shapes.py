from typing import Annotated, Literal

from advanced_alchemy.filters import OrderBy
from litestar.params import QueryParameter

from . import examples


async def provide_order_by_shapes(
    field_name: Annotated[
        str,
        QueryParameter(
            name="orderBy",
            examples=[examples.e_sequence, examples.e_distance],
        ),
    ] = "sequence",
    sort_order: Annotated[
        Literal["asc", "desc"],
        QueryParameter(
            name="sortOrder",
            examples=[examples.e_asc, examples.e_desc],
        ),
    ] = "asc",
) -> OrderBy:
    """Add order by for shapes.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    field_name : str
        Field to order on.
    sort_order : Literal["asc", "desc"]
        Direction to sort.
    """

    return OrderBy(field_name, sort_order)
