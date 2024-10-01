from litestar.params import Parameter
from litestar.repository.filters import OrderBy

from . import examples


async def provide_order_by_shapes(
    field_name: str = Parameter(
        query="orderBy",
        default="sequence",
        required=False,
        examples=[examples.e_sequence, examples.e_distance],
    ),
    sort_order: str = Parameter(
        query="sortOrder", default="asc", required=False, examples=[examples.e_asc, examples.e_desc]
    ),
) -> OrderBy:
    """Add order by for shapes.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    field_name : str
        Field to order on.
    sort_order : str
        Direction to sort.
    """

    return OrderBy(field_name, sort_order)
