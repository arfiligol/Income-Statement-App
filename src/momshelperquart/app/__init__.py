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

    from .lawyer_income_detail import lawyer_income_detail as lawyer_income_detail_blueprint # 律師收入明細 -> 程式處理後的第一個工作表(第一個功能)
    app.register_blueprint(lawyer_income_detail_blueprint, url_prefix = "/lawyer_income_detail")


    return app