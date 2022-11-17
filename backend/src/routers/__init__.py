from sanic import Blueprint

from .auth import router as auth_router

routers: tuple[Blueprint] = (auth_router,)
