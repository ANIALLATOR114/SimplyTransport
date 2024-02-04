from litestar.response import Template
from litestar import Request, Response
from litestar.exceptions import HTTPException


def check_if_website(request: Request) -> bool:
    """Check if the request is for the website."""
    return "text/html" in request.headers.get("accept", "")


def handle_404(_: Request, exc: HTTPException) -> Response | Template:
    if check_if_website(_):
        return Template(
                template_name="errors/404.html",
                status_code=exc.status_code,
                context={},
            )
    else:
        return Response(status_code=404, 
            content={
            "path": _.url.path,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },)


def website_exception_handler(_: Request, exc: HTTPException) -> Template:
    """Website handler for exceptions subclassed from HTTPException."""
    status_code = getattr(exc, "status_code", 500)

    match status_code:
        case 500:
            return Template(
                template_name="errors/500.html",
                status_code=status_code,
                context={},
            )
        case _:
            return Template(
                template_name="errors/500.html",
                status_code=status_code,
                context={},
            )