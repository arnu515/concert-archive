import os

from sanic import Sanic, json

from src.util.db import db

app = Sanic("concert_backend")

if os.getenv("DEV"):
    app.config.CORS = True
    app.config.CORS_ALLOW_HEADERS = "*"
    app.config.CORS_ALWAYS_SEND = True
    app.config.CORS_AUTOMATIC_OPTIONS = True
    app.config.CORS_METHODS = "*"
    app.config.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


@app.route("/")
async def index(_):
    await db.oauthcodes.create({"code": "test", "user": {"connect": {"id": "clakdvx470000le9vh2c3i1tb"}}})
    return json({"message": "Hello, world!"})
