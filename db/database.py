import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from .models import Base


load_dotenv()

def get_session():
    # sqlite db path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_filename = os.getenv("DATABASE_FILENAME", "sqlite_db.db")
    db_dir = os.path.join(base_dir, "data", "db")
    db_file_path = os.path.join(db_dir, db_filename)
    # 檢查目錄是否存在，如果不存在則創建
    if not os.path.exists(db_dir):
        logging.info("偵測到 SQLite 資料庫目錄不存在，自動創建...")
        os.makedirs(db_dir)
    
    # db connection
    engine = create_engine(f"sqlite:///{db_file_path}")
    Base.metadata.create_all(engine)

    # sessionmaker 是 SQLAlchemy 的一個工廠函數，用於創建 Session 對象，這些對象代表了程序與數據庫的一次對話。
    # bind=engine 參數將 sessionmaker 與特定的數據庫引擎綁定，確保所有透過 Session 進行的操作都使用這個引擎與數據庫通信。
    Session = sessionmaker(bind = engine) # 創建與數據庫引擎綁定的 Session 工廠函數
    return Session()