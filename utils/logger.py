import logging
from colorlog import ColoredFormatter
from dotenv import load_dotenv
import os

load_dotenv()

def setup_logger():
    # 獲取日誌級別的環境變數，如果讀取到的值沒有對應級別，設為 DEBUG LEVEL
    log_level_str = os.getenv("LOGGER_LEVEL", "DEBUG")
    log_level = getattr(logging, log_level_str.upper(), logging.DEBUG)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 創建一個 handler 輸出到控制台
    # 創建一個控制台日誌處理器，並設定捕獲所有 'log_level' 及以上級別的日誌
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # 定義 handler 使用的日誌格式
    # 使用 colorlog 的 ColoredFormatter 為日誌信息添加顏色
    # 日誌格式包括：日誌級別（帶顏色）、消息本身
    # log_colors 定義每個日誌級別的顏色
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    
    # 將格式化器設置給日誌處理器，並將處理器添加到 logger
    ch.setFormatter(formatter)
    logger.addHandler(ch)