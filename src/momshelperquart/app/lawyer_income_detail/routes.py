import logging
from quart import render_template

from . import lawyer_income_detail

@lawyer_income_detail.get("/")
async def index() -> str:
    return await render_template("lawyer_income_detail.html")