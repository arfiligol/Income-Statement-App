import logging

from . import main

@main.route("/")
async def index() -> str:
    return "Welcome to the Mom Package Website!"