
# Controllers
from controllers import MainController

# Application Models

# CRUD
from db.database import get_session

# Utils
from utils.logger import setup_logger



def run():
    # 初始化 logger
    setup_logger()

    session = get_session()
    main_view_controller = MainController()



if __name__ == "__main__":
    run()