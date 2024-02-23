from litestar import Router
from litestar.static_files import create_static_files_router
from litestar.datastructures.headers import CacheControlHeader
from .constants import STATIC_DIR, APP_DIR

# Root level static files are served from the root controller (/favicon.ico, /robots.txt, etc.)

def create_static_router() -> Router:
    """
    Creates a static router for serving static files.

    Returns:
        Router: The static router.
    """
    return create_static_files_router(
        path=f"/{STATIC_DIR}",
        directories=[f"./{APP_DIR}/{STATIC_DIR}/{STATIC_DIR}"],
        name=STATIC_DIR,
        cache_control=CacheControlHeader(max_age=86400*90))
