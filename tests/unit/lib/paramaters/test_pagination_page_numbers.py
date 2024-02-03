import pytest
from SimplyTransport.lib.parameters.pagination_page_numbers import generate_pagination_pages

@pytest.mark.parametrize(
    "current_page, total_pages, expected",
    [
        (1, 5, [1, 2, 3, 4, 5]),
        (1, 1, [1]),
        (1, 2, [1, 2]),
        (2, 3, [1, 2, 3]),
        (3, 3, [1, 2, 3]),
        (5, 5, [1, 2, 3, 4, 5]),
        (3, 10, [1, 2, 3, 4, 10]),
        (1, 10, [1, 2, 3, 4, 10]),
        (10, 10, [1, 7, 8, 9, 10]),
        (2, 10, [1, 2, 3, 4, 10]),
        (9, 10, [1, 7, 8, 9, 10]),
        (50, 100, [1, 49, 50, 51, 100]),
    ],
)
def test_generate_pagination_pages(current_page, total_pages, expected):
    assert generate_pagination_pages(current_page, total_pages) == expected