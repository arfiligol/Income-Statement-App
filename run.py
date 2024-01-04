from app import create_app
from utils.logger import setup_logger

app = create_app()

if __name__ == "__main__":
    setup_logger()
    app.run(debug = True)