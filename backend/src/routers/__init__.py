from sanic import Blueprint

from .auth import router as auth_router
from .stages import router as stages_router

routers: tuple[Blueprint] = (auth_router, stages_router)
