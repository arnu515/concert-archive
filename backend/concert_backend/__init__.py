from sanic import file
from sanic.exceptions import NotFound
import pathlib
import os

from .application import app
from .routers import routers
from .util.db import db

STATIC_DIR = str(pathlib.Path(__file__).parent.parent / "static")


@app.listener("before_server_start")
async def setup_db(app, loop):  # noqa
    print("Connected to database")
    await db.connect()


@app.listener("after_server_stop")
async def close_db(app, loop):  # noqa
    print("Disconnected from database")
    await db.disconnect()

app.blueprint(routers)


print(os.path.exists(STATIC_DIR))
if os.path.exists(STATIC_DIR):
    app.static("/", STATIC_DIR, name="serve files")

    @app.get("/")
    async def serve_index_html(_):
        return await file(os.path.join(STATIC_DIR, "index.html"), max_age=7 * 24 * 60 * 60)

    @app.get("/favicon.png")
    async def serve_favicon(_):
        return await file(os.path.join(STATIC_DIR, "favicon.png"), max_age=7 * 24 * 60 * 60)

    @app.exception(NotFound)
    async def serve_index_html(_1, _2):
        print("404")
        return await file(os.path.join(STATIC_DIR, "index.html"), max_age=7 * 24 * 60 * 60)
