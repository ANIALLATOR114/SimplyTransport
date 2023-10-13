from litestar import Controller, get

__all__ = [
    "sampleController",
]


class SampleController(Controller):
    @get("/")
    async def root(self) -> str:
        return "SampleController"

    @get("/{id:int}")
    async def route_by_id(self, id: int) -> str:
        return f"SampleController: {id}"
