from quart import Blueprint

lawyer_income_detail = Blueprint("lawyer_income_detail", __name__, template_folder = "templates")

from . import routes