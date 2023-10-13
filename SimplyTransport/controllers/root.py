from litestar import Controller, get

__all__ = [
    "rootController",
]


class RootController(Controller):
    @get("/")
    async def root(self) -> str:
        return "Hello World"

    @get("/healthcheck")
    async def healthcheck(self) -> str:
        return "OK"
