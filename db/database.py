from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from dotenv import load_dotenv
import os

load_dotenv()

def get_session():
    db_file = os.getenv("DATABASE_URL")
    if not (db_file):
        db_file = "sqlite_db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)

    # sessionmaker 是 SQLAlchemy 的一個工廠函數，用於創建 Session 對象，這些對象代表了程序與數據庫的一次對話。
    # bind=engine 參數將 sessionmaker 與特定的數據庫引擎綁定，確保所有透過 Session 進行的操作都使用這個引擎與數據庫通信。
    Session = sessionmaker(bind = engine) # 創建與數據庫引擎綁定的 Session 工廠函數
    return Session()