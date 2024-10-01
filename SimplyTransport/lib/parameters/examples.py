from litestar.openapi.spec.example import Example

e_sequence = Example(
    summary="Order by sequence",
    description="Order by sequence of shapes.",
    value="sequence",
)
e_distance = Example(
    summary="Order by distance",
    description="Order by distance of shapes.",
    value="distance",
)
e_asc = Example(
    summary="Ascending order",
    description="Ascending order.",
    value="asc",
)
e_desc = Example(
    summary="Descending order",
    description="Descending order.",
    value="desc",
)
