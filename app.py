from litestar import Litestar, get


@get("/")
async def index() -> str:
    return "Hello, world!"

app = Litestar([index])