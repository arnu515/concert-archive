from sanic import file
from sanic.exceptions import NotFound
from concert_backend.application import app
import os
#
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static")


@app.exception(NotFound)
async def serve_index_html(_1, _2):
    return await file(os.path.join(STATIC_DIR, "index.html"))


app.static("/", "./static")
