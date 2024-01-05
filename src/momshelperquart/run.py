from momshelperquart.app import create_app
from momshelperquart.utils.logger import setup_logger

app = create_app()

def run() -> None:
    setup_logger()
    app.run(debug = True)