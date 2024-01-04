from . import main

@main.route("/")
async def index():
    return "Welcome to the Mom Package Website!"