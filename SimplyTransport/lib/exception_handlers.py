from litestar import Request, Response
from litestar.exceptions import HTTPException
from litestar.response import Template

from SimplyTransport.lib.logging.logging import provide_logger

logger = provide_logger(__name__)


def check_if_website(request: Request) -> bool:
    """
    Check if the request accepts HTML content.

    Args:
        request (Request): The request object.

    Returns:
        bool: True if the request accepts HTML content, False otherwise.
    """
    return "text/html" in request.headers.get("accept", "")


def handle_404(_: Request, exc: HTTPException) -> Response | Template:
    """
    Handle the 404 error by returning a response or template based on the request.

    Args:
        _: The request object.
        exc: The HTTPException object representing the 404 error.

    Returns:
        If the request is for a website, returns a Template object with the 404.html template,
        otherwise returns a Response object with the 404 status code and error details.
    """
    if check_if_website(_):
        return Template(
            template_name="errors/404.html",
            status_code=exc.status_code,
            context={},
        )
    else:
        return Response(
            status_code=404,
            content={
                "path": _.url.path,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )


def exception_handler(request: Request, exc: HTTPException) -> Response | Template:
    """
    Handle exceptions raised during request processing.

    Args:
        _: The request object.
        exc: The exception object raised during request processing.

    Returns:
        If the request is for a website, returns a Template object with the appropriate error page.
        If the request is for an API, returns a Response object with the error details.

    """
    status_code = getattr(exc, "status_code", 500)

    if check_if_website(request):
        logger.bind(path=request.url.path, code=status_code).exception("Website Exception", exc_info=exc)
        return Template(
            template_name="errors/500.html",
            status_code=status_code,
            context={},
        )
    else:
        logger.bind(path=request.url.path, code=status_code).exception("API Exception", exc_info=exc)
        return Response(
            status_code=status_code,
            content={
                "path": request.url.path,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )
