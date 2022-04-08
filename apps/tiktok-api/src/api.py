from api import config, logging
from src.status import routes as status_routes
from src.tiktok import routes as tiktok_routes
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

log = logging.get_logger(__name__)


# async def startup():
#     await db.connect()


# async def shutdown():
#     await db.disconnect()


async def root(request: Request):
    return JSONResponse({"status": "ok"})


CORS_PARAMS_BY_ENVIRONMENT = {
    "prod": {"allow_origins": "*"},
    "nonprod": {"allow_origins": "*"},
}


routes = [
    Route("/", endpoint=root),
    Mount("/tiktok", routes=tiktok_routes),
    Mount("/status", routes=status_routes),
]

middleware = [
    Middleware(ProxyHeadersMiddleware),
    Middleware(
        CORSMiddleware,
        allow_methods=["*"],
        allow_headers=["Authorization"],
        **CORS_PARAMS_BY_ENVIRONMENT.get(config.ENVIRONMENT, {"allow_origins": "*"}),
    ),
]


app = Starlette(
    debug=config.DEBUG,
    routes=routes,
    middleware=middleware,
    # exception_handlers=exception_handlers,
    # on_startup=[startup],
    # on_shutdown=[shutdown],
)
