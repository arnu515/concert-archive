from .application import app
from .routers import routers
from .util.db import db


@app.listener("before_server_start")
async def setup_db(app, loop):  # noqa
    print("Connected to database")
    await db.connect()


@app.listener("after_server_stop")
async def close_db(app, loop):  # noqa
    print("Disconnected from database")
    await db.disconnect()


app.blueprint(routers)
