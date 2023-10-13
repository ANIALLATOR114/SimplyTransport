from typing import Any

import uvicorn
from litestar import Litestar

from SimplyTransport.controllers import create_api_router, create_views_router

__all__ = ["create_app"]

def create_app(**kwargs: Any) -> Litestar:

    return Litestar(
        route_handlers=[create_api_router(), create_views_router()],
    )

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )