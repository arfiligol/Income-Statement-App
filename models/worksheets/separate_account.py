import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Border, Side, Alignment
import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views import MainView

class SeparateAccountsWorksheet:
    def __init__(self, workbook_path, tk_root: "MainView"):
        if not os.path.exists(workbook_path):
            self.wb = Workbook()
            self.is_new_workbook = True
            self.save(workbook_path)
        else:
            self.is_new_workbook = False
            self.wb = load_workbook(workbook_path)
        self.workbook_path = workbook_path
        self.sheet_title = "程式RUN後檔案"
        self.headers = ["日期", "摘要", "借方金額", "貸方金額", "承辦律師"]
        self.root = tk_root
        self.init_ws()
        

    def init_ws(self):
        # 如果是新建 Workbook 而有預設建立的工作表，刪除它
        if self.is_new_workbook:
            self.wb.remove(self.wb["Sheet"])

        # 如果目標工作表存在則使用它，否則創建一個新的工作表
        if self.sheet_title in self.wb.sheetnames:
            # 確認是否覆蓋掉已有的工作表
            response = messagebox.askyesno("工作表存在", f"工作表'{self.sheet_title}' 已經存在，你想要覆蓋它嗎？")
            if response:
                # 刪除創建新的
                self.wb.remove(self.wb[self.sheet_title])
                self.create_worksheet()
            else:
                # 使用已有的工作表
                self.ws = self.wb[self.sheet_title]

        else: # 沒有該工作表，直接創建一個新的
            self.create_worksheet()

    def create_worksheet(self):
        self.ws = self.wb.create_sheet(self.sheet_title)
        self.format_worksheet()
        self.save(self.workbook_path)
    
    def save(self, filename):
        try:
            self.wb.save(filename)
    
        except PermissionError as err:
            messagebox.showerror("無法儲存變更到檔案", "請確認目標檔案是否已經關閉，若透過其他程式開啟該檔案，則無法在此程式更改該檔案！")
            print(err)

    # 用於格式化、設定工作表樣貌
    def format_worksheet(self):
        letters = ["A", "B", "C", "D", "E"]
        # 設定欄寬
        width_offset = 2
        self.ws.column_dimensions["A"].width = 15.9 + width_offset
        self.ws.column_dimensions["B"].width = 50.5 + width_offset
        self.ws.column_dimensions["C"].width = 13 + width_offset
        self.ws.column_dimensions["D"].width = 15.9 + width_offset
        self.ws.column_dimensions["E"].width = 15.9 + width_offset


        # 建立欄位
        for col, letter in enumerate(letters, start = 1):
            self.ws.merge_cells(f"{letter}1:{letter}2")
            cell = self.ws.cell(row = 1, column=col)

            # 設定 Cell
            cell.value = self.headers[col - 1] # 給值
            cell.font = Font(name = "微軟正黑體", size = 13, )
            for row in self.ws["A1:E2"]:
                for single_cell in row:
                    single_cell.border = Border(left=Side(style='thin'), 
                     right=Side(style='thin'), 
                     top=Side(style='thin'), 
                     bottom=Side(style='thin'))
            cell.alignment = Alignment(horizontal = "center", vertical = "center")

    
    def write_data_to_worksheet(self, data_rows):
        first_empty_row = self.ws.max_row + 1
        # 檢測是否有資料
        if (first_empty_row != 3):
            overWriteOldData = messagebox.askyesno("偵測到工作表'程式RUN後檔案'已有資料，是否覆寫？")
            if overWriteOldData:
                # 若決定覆寫，將數據寫入第一行設在 row = 2
                first_empty_row = 3
        
        # 開始寫入資料到工作表
        for row_index, row in enumerate(data_rows, start=0): # 因為 first_empty_row 會設為最新空格，因此 row_index 從 0 開始
            for column_index in range(0, len(self.headers), 1): # column 從零開始算
                cell = self.ws[first_empty_row + row_index][column_index]
                cell.value = row[column_index]
                
                cell.font = Font(name = "Courier New", size = 13)
                cell.border = Border(left=Side(style='thin'), 
                     right=Side(style='thin'), 
                     top=Side(style='thin'), 
                     bottom=Side(style='thin'))
                if column_index == 4:
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrapText=True)
                else:
                    cell.alignment = Alignment(vertical="bottom", wrapText=True)
        
        self.save(self.workbook_path)