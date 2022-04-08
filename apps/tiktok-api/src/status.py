from starlette.responses import JSONResponse
from starlette.routing import Route

from src.config import ENVIRONMENT
from src.exceptions import NotFound


async def ok(request):
    """Return OK
    ---
    description: Return OK
    responses:
        200:
            description: Returns OK
    """
    return JSONResponse({"status": "ok", "environment": ENVIRONMENT})


async def not_found(request):
    """Return Not Found
    ---
    description: Return Not Found
    responses:
        404:
            description: Returns not found
    """
    raise NotFound()


routes = [
    Route("/ok", ok, methods=["GET"]),
    Route("/not-found", not_found, methods=["GET"]),
]
