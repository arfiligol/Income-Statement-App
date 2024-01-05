import logging
from quart import render_template

from . import main

@main.get("/")
async def index() -> str:
    return await render_template("main.html")