from __future__ import annotations

# Controllers
from controllers import MainController

# Utils
from utils.logger import setup_logger


def run() -> None:
    # 初始化 logger
    setup_logger()

    MainController()



if __name__ == "__main__":
    run()
