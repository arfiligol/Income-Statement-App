import logging
import sys
import os
from pathlib import Path

def get_root_dir_path() -> Path:
    # 如果是使用 PyInstaller 打包後執行的情境，回傳執行檔執行時的資料夾作為根目錄
    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
    else: # 如果是其他執行情況，例如直接執行 run.py
        root_dir = Path(__file__).resolve().parent.parent # 回傳此檔案路徑的上一層 => 與 run.py 同層
    
    logging.debug(f"取得執行根目錄路徑: {root_dir}")
    return root_dir