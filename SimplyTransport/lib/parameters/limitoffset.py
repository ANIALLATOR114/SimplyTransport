from typing import Annotated

from advanced_alchemy.filters import LimitOffset
from litestar.params import QueryParameter


async def provide_limit_offset_pagination(
    current_page: Annotated[int, QueryParameter(name="currentPage", ge=1)] = 1,
    page_size: Annotated[int, QueryParameter(name="pageSize", ge=1, le=100)] = 20,
) -> LimitOffset:
    """Add offset/limit pagination.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (current_page - 1))
