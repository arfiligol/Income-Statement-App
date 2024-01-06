import logging
import os
import pandas as pd
from tkinter import filedialog, messagebox

from .base import BaseController
from views import MainView
from db.crud.lawyer import insert_unique_lawyers, fetch_all_lawyers
from models.worksheets import SeparateAccountsWorksheet
from utils import check_filename_is_valid

class MainController(BaseController):
    def __init__(self):
        super().__init__()
        self.window:MainView = MainView(self)
        self.window.mainloop()

        # Attributes
        self.selected_file_name = None
        self.output_dir = None

    
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
    
    def choose_output_dir(self):
        folder_is_not_selected = True
        while (folder_is_not_selected):
            logging.debug("正在詢問用戶輸出檔案的資料夾...")
            folder_path = filedialog.askdirectory()

            if (folder_path):
                logging.info(f"用戶選擇輸出位置: {folder_path}")
                self.output_dir = folder_path
                self.window.labels["OutputDirPathLabel"].config(text = folder_path)
                folder_is_not_selected = False
            
            else:
                break
    
    def separate_the_ledger(self):
        # 先檢查【輸出資料夾】是否有給，若無輸出檔名，預設為【output.xlsx】
        if (self.output_dir == None):
            messagebox.showerror("錯誤", "請先選擇要輸出的資料夾！")
            return
        
        output_file_name = self.window.entries["OutputFileNameEntry"].get()
        if (output_file_name == "輸入輸出檔名" or output_file_name.replace(" ", "") == ""): # 如果移除所有空格為空 => 無名稱
            messagebox.showinfo("說明", "沒有給予輸出檔名，將使用 'output' 作為檔名")
            output_file_name = "output"
        elif (check_filename_is_valid(output_file_name)):
            messagebox.showerror("錯誤", "輸出檔名包含不合法字元")
            return
        output_file_name = self.output_dir + "/" + output_file_name + ".xlsx"
        logging.info(f"資料將儲存於: {output_file_name}")
            


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
        total_debit = 0
        total_credit = 0
        ready_for_data = False
        for row in origin_array:
            if row[9] != "備註" and not ready_for_data:
                continue
            elif row[9] == "備註":
                ready_for_data = True
                continue
            
            if (ready_for_data):
                # 取資料做處理
                date = row[0] # 日期
                if (pd.isna(date)):
                    continue
                abstract = row[1] # 摘要
                debit = row[2] # 借方金額
                credit = row[3] # 貸方金額
                debit_or_credit = row[4] # 借 or 貸
                balance = row[5]
                department = row[8] # 部門
                remark = row[9] # 用來解析

                # 將律師代碼拆分，並寫入資料庫
                lawyer_code_list = remark.split(' ')
                # 移除空元素
                filtered_code_list = [item for item in lawyer_code_list if item]
                insert_unique_lawyers(filtered_code_list) # 將 Lawyer 寫入資料庫紀錄

                # 處理金額，若為 Nan 則視為零元
                if (pd.isna(debit)):
                    debit = 0
                if (pd.isna(credit)):
                    credit = 0

                # 總計整張表的 debit 跟 credit
                
                # 有幾個 Lawyer 就拆分成幾筆資料
                for code in filtered_code_list:
                    # 金額四捨五入至整數（元）
                    separate_debit = round(float(debit) / len(filtered_code_list))
                    separate_credit = round(float(credit) / len(filtered_code_list))
                    # 統計整張表的數值
                    total_debit += separate_debit
                    total_credit += separate_credit

                    data.append([date, abstract, department, separate_debit, separate_credit, code]) 


        try:
            target_sheet = SeparateAccountsWorksheet(output_file_name, self)
            target_sheet.write_data_to_worksheet(data, total_debit=total_debit, total_credit=total_credit) # 寫入分帳
            
            # 取出所有 Lawyer Code，進行遍歷
            lawyer_credits = []
            lawyers = fetch_all_lawyers()
            for lawyer in lawyers:
                lawyer_total_credit = 0
                for row in data:
                    if (row[4] == lawyer.code):
                        lawyer_total_credit += row[3]
                
                lawyer_credits.append({
                    "lawyer_code": lawyer.code,
                    "lawyer_total_credit": lawyer_total_credit,
                })


            # 都沒問題，處理完畢，用 Label 告知使用者
            hintLabel = self.window.labels["DealingWorkIsDoneLabel"]
            hintLabel.config(text = f"處理完畢，檔案已寫入到路徑: {output_file_name}")
            hintLabel.grid(row = 4, column = 1, pady = 10)
        except Exception as err:
            messagebox.showerror("寫入資料時發生錯誤", "請聯繫管理員！")
            logging.error(f"寫入資料到 'SeparateAccountsWorksheet' 時發生錯誤... Error: {err}")