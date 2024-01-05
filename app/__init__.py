from quart import Quart
from .config import Config

def create_app() -> Quart:

    # 傳遞 __name__ 的主要目的是為了確定應用的根目錄位置， __name__ 是 Python 的一個內置變量，他表示當前模塊的名稱
    app = Quart(__name__)

    # 註冊 Config
    app.config.from_object(Config)

    # 在這裡引入 Blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app