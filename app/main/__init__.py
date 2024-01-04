from quart import Blueprint, render_template

main = Blueprint("main", __name__)

from . import routes