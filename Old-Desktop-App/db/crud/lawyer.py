from sqlalchemy.exc import IntegrityError
from ..models import Lawyer
from ..database import get_session

def fetch_all_lawyers():
    session = get_session()

    try:
        lawyers = session.query(Lawyer).all()

        # 關閉 session
        session.close()
        return lawyers
    
    except Exception as err:
        print(f"An error occurred: {err}")

        # 關閉 session
        session.close()
        return []
    
    
    

def insert_unique_lawyers(code_list):
    session = get_session()

    # 處理陣列中的每個 Lawyer
    for code in code_list:
        new_lawyer = Lawyer(code = code)
        session.add(new_lawyer)

        try:
            # 嘗試提交，如果 Lawyer 已存在，將引發異常
            session.commit()
        except IntegrityError:
            # 如果 IntegrityError 被捕獲，表示違反了數據庫的完整性約束。

            # 例如：
            # - 嘗試插入已經存在於具有 UNIQUE 約束的列（如主鍵或唯一索引）的值。
            # - 外鍵不存在於關聯的表中。
            # - 非空約束列接收到了 null 值。
            # - 某個列的值未通過設定的 CHECK 約束條件。
            session.rollback()  # 回滾事務以保持會話的一致性
            # 處理異常，例如通過用戶界面報告錯誤或記錄錯誤信息
    
    # 關閉 session 避免堆積
    session.close()