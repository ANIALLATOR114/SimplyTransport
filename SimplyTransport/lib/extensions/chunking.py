from collections.abc import Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")


def chunk_list(lst: Sequence[T], chunk_size: int) -> Iterator[Sequence[T]]:
    """Split a sequence into chunks of specified size.


    Args:
        lst: Any sequence (list, tuple, etc)
        chunk_size: Size of each chunk

    Returns:
        Iterator yielding subsequences of the input

    Raises:
        ValueError: If chunk_size <= 0
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return (lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size))
