import os
import sys
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from .models import Base
from momshelperquart.utils.get_path import get_root_dir_path

load_dotenv()

def get_session():
    # sqlite db path
    base_dir = get_root_dir_path()
    db_filename = os.getenv("DATABASE_FILENAME", "sqlite_db.db")
    db_dir = base_dir / "data" / "db"
    db_file_path = db_dir / db_filename
    # 檢查目錄是否存在，如果不存在則創建
    db_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"SQLite 資料庫目錄確認存在或已創建於：{db_dir}")

    
    # db connection
    engine = create_engine(f"sqlite:///{db_file_path}")
    Base.metadata.create_all(engine)

    # sessionmaker 是 SQLAlchemy 的一個工廠函數，用於創建 Session 對象，這些對象代表了程序與數據庫的一次對話。
    # bind=engine 參數將 sessionmaker 與特定的數據庫引擎綁定，確保所有透過 Session 進行的操作都使用這個引擎與數據庫通信。
    Session = sessionmaker(bind = engine) # 創建與數據庫引擎綁定的 Session 工廠函數
    return Session()