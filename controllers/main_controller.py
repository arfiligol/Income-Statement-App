import logging
import os
import pandas as pd
from tkinter import filedialog, messagebox

from .base import BaseController
from views import MainView
from db.crud.lawyer import insert_unique_lawyers, fetch_all_lawyers
from models.worksheets import SeparateAccountsWorksheet

class MainController(BaseController):
    def __init__(self):
        super().__init__()
        self.window:MainView = MainView(self)
        self.window.mainloop()

        # Attributes
        self.selected_file_name = None

    
    def open_excel_file(self):
        file_is_not_selected = True
        while (file_is_not_selected):
            logging.debug("正在詢問用戶要開啟的檔案...")
            filename = filedialog.askopenfilename()


            if (filename): # 確定有選擇檔案
                # 檢查副檔名是否與 Excel 相關
                if (os.path.splitext(filename)[1] not in [".xls", ".xlsx"]):
                    messagebox.showwarning("警告", "選擇的檔案不是 .xls 或 .xlsx，請重新選擇！")
                    continue
                else:
                    logging.info(f"用戶選擇檔案: {filename}")
                    self.selected_file_name = filename
                    self.window.labels["OpenedFilePathLabel"].config(text = filename)
                    file_is_not_selected = False
            
            else: # 用戶案取消
                logging.debug("用戶取消選擇檔案！")
                break
    
    def separate_the_ledger(self):
        logging.info(f"開始處理檔案: {self.selected_file_name}, 執行動作: 'separate_the_ledger()'")
        xls = pd.ExcelFile(self.selected_file_name)
        sheet_names = xls.sheet_names

        if ("明細分類帳(依科目+部門)-0_備註欄加上承辦律師" not in sheet_names):
            messagebox.showwarning("錯誤", "缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
            logging.warning("缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
            return
        
        origin_sheet = pd.read_excel(self.selected_file_name, sheet_name="明細分類帳(依科目+部門)-0_備註欄加上承辦律師")
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
                insert_unique_lawyers(filtered_code_list) # 將 Lawyer 寫入資料庫紀錄
                
                # 有幾個 Lawyer 就拆分成幾筆資料
                for code in filtered_code_list:
                    data.append([date, abstract, float(debit), float(credit) / len(filtered_code_list), code])

        print(data)
        target_sheet = SeparateAccountsWorksheet("data/output2.xlsx", self)
        target_sheet.write_data_to_worksheet(data)
        
        # 取出所有 Lawyer Code，進行遍歷
        lawyer_credits = []
        lawyers = fetch_all_lawyers()
        for lawyer in lawyers:
            total_credit = 0
            for row in data:
                if (row[4] == lawyer.code):
                    total_credit += row[3]
            
            lawyer_credits.append({
                "lawyer_code": lawyer.code,
                "total_credit": total_credit,
            })
        
        print(lawyer_credits)        