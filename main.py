import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from models.worksheet import SeparateAccountsWorksheet

def open_file():
    global selected_file_name
    file_is_not_selected = True
    while (file_is_not_selected):
        filename = filedialog.askopenfilename()

        if (filename): # 確定有選擇檔案

            if (os.path.splitext(filename)[1] not in ['.xls', '.xlsx']): # 檢查副檔名是否與 Excel 相關檔案有關
                messagebox.showwarning("警告", "選擇的檔案不是 .xls 或 .xlsx，請重新選擇！")
                continue

            selected_file_name = filename
            file_label.config(text=f"選擇的檔案: {filename}")
            file_is_not_selected = False
        else: # 如果按取消
            break
    

# Database Part
Base = declarative_base()

class Code(Base):
    __tablename__ = "codes"
    code = Column(String, primary_key=True)

def insert_unique_codes(code_list, db_file):
    # Connect to DB
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 處理陣列中的每個 Code
    for code in code_list:
        new_code = Code(code = code)
        session.add(new_code)
        try:
            # 嘗試提交(如果 Code 已存在，將引發異常)
            session.commit()
        except IntegrityError:
            # 如果 Code 已存在，回滾繪畫
            session.rollback()
    
    # 關閉 Session
    session.close()

# def copyWorksheetStyle(source_sheet, destinate_sheet): # 直接給 openpyxl 的 sheet object
    

def separate_the_ledger(excel_filename, tk_root):
    print(f"Start Handling the Excel File: {excel_filename}")
    xls = pd.ExcelFile(excel_filename)
    sheet_names = xls.sheet_names

    if ("明細分類帳(依科目+部門)-0_備註欄加上承辦律師" not in sheet_names):
        messagebox.showwarning("錯誤", "缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
        print("缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
        return
    
    origin_sheet = pd.read_excel(excel_filename, sheet_name="明細分類帳(依科目+部門)-0_備註欄加上承辦律師")
    origin_array = origin_sheet.values
    if (len(origin_array[0]) != 10):
        messagebox.showerror("錯誤", "格式與當初給定的不一樣，原本偵測到十個欄位，現在偵測到: {} 個欄位\n請檢查檔案【明細分類帳(依科目+部門)-0_備註欄加上承辦律師】中的內容".format(len(origin_array[0])))
        return
    

    data = []

    ready_for_data = False
    for row in origin_array:
        if row[9] != "備註" and not ready_for_data:
            continue
        elif row[9] == "備註":
            ready_for_data = True
            continue
        
        if (ready_for_data):
            date = row[0] # 日期
            if (pd.isna(date)):
                continue
            abstract = row[1] # 摘要
            debit = row[2] # 借方金額
            credit = row[3] # 貸方金額
            debit_or_credit = row[4] # 借 or 貸
            balance = row[5]
            remark = row[9]

            lawyer_code_list = remark.split(' ')
            # 移除空元素
            filtered_code_list = [item for item in lawyer_code_list if item]
            insert_unique_codes(filtered_code_list, "lawyer_data.db") # 將 Code 寫入資料庫紀錄
            
            # 有幾個 Code 就拆分成幾筆資料
            for code in filtered_code_list:
                data.append([date, abstract, float(debit), float(credit) / len(filtered_code_list), code])

    print(data)
    target_sheet = SeparateAccountsWorksheet("output2.xlsx", tk_root)
    target_sheet.write_data_to_worksheet(data)
    return data




root = tk.Tk()
root.geometry("400x200")

open_file_button = tk.Button(root, text="選擇檔案", command=open_file)
open_file_button.pack(pady=10)

file_label = tk.Label(root, text="尚未選擇檔案")
file_label.pack(pady=10)

confirm_button = tk.Button(root, text="確認", command=lambda:separate_the_ledger(selected_file_name, root))
confirm_button.pack(pady=10)

root.mainloop()
