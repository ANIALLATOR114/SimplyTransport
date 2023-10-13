from litestar import Litestar, get


@get("/")
async def index() -> str:
    return "Hello, world this is working!"

app = Litestar(
    [
    index
    ]
    )