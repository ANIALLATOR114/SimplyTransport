from litestar import Controller, get
from litestar.response import Template

__all__ = [
    "RootController",
]


class RootController(Controller):
    @get("/")
    async def root(self) -> Template:
        return Template(template_name="index.html")
    
    @get("/about")
    async def about(self) -> Template:
        return Template(template_name="about.html")
    
    @get("/apidocs")
    async def api_docs(self) -> Template:
        return Template(template_name="api_docs.html")
    
    @get("/healthcheck")
    async def healthcheck(self) -> str:
        return "OK"
    
    @get("/stops")
    async def stop(self) -> Template:
        return Template("gtfs_search/stop_search.html")
    
    @get("/routes")
    async def route(self) -> Template:
        return Template("gtfs_search/route_search.html")
    