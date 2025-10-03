from __future__ import annotations

import logging
import os
from tkinter import filedialog, messagebox
from typing import List, Optional, Tuple

import pandas as pd
from pandas import DataFrame

from db.crud.lawyer import fetch_all_lawyers, insert_unique_lawyers
from models.worksheets import SeparateAccountsWorksheet
from utils import check_filename_is_valid
from views import MainView

from .base import BaseController


class LedgerFormatError(Exception):
    """Raised when the source worksheet format does not meet expectations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MainController(BaseController):
    def __init__(self) -> None:
        super().__init__()

        # Attributes
        self.selected_file_name: Optional[str] = None
        self.output_dir: Optional[str] = None
        # Create Window
        self.window = MainView(self)
        self.window.mainloop()

    
    def open_excel_file(self) -> Optional[str]:
        file_is_not_selected = True
        while file_is_not_selected:
            logging.debug("正在詢問用戶要開啟的檔案...")
            filename = filedialog.askopenfilename()

            if filename: # 確定有選擇檔案
                # 檢查副檔名是否與 Excel 相關
                if os.path.splitext(filename)[1] not in [".xls", ".xlsx"]:
                    messagebox.showwarning("警告", "選擇的檔案不是 .xls 或 .xlsx，請重新選擇！")
                    continue
                else:
                    logging.info(f"用戶選擇檔案: {filename}")
                    self.selected_file_name = filename
                    file_is_not_selected = False
                    return filename
            
            else: # 用戶案取消
                logging.debug("用戶取消選擇檔案！")
                break
        return None
    
    def choose_output_dir(self) -> Optional[str]:
        folder_is_not_selected = True
        while folder_is_not_selected:
            logging.debug("正在詢問用戶輸出檔案的資料夾...")
            folder_path = filedialog.askdirectory()

            if folder_path:
                logging.info(f"用戶選擇輸出位置: {folder_path}")
                self.output_dir = folder_path
                folder_is_not_selected = False
                return folder_path
            else:
                break
        return None
    
    def separate_the_ledger(self) -> None:
        # 先檢查【輸出資料夾】是否有給，若無輸出檔名，預設為【output.xlsx】
        if self.output_dir is None:
            messagebox.showerror("錯誤", "請先選擇要輸出的資料夾！")
            return

        output_file_name = self.window.output_filename.get()
        if output_file_name == "輸入輸出檔名" or output_file_name.replace(" ", "") == "": # 如果移除所有空格為空 => 無名稱
            messagebox.showinfo("說明", "沒有給予輸出檔名，將使用 'output' 作為檔名")
            output_file_name = "output"
        elif check_filename_is_valid(output_file_name):
            messagebox.showerror("錯誤", "輸出檔名包含不合法字元")
            return
        if self.selected_file_name is None:
            messagebox.showerror("錯誤", "請先選擇來源檔案！")
            return

        output_file_name = os.path.join(self.output_dir, output_file_name + ".xlsx")
        logging.info(f"資料將儲存於: {output_file_name}")
            


        logging.info(f"開始處理檔案: {self.selected_file_name}, 執行動作: 'separate_the_ledger()'")
        xls = pd.ExcelFile(self.selected_file_name)
        sheet_names = xls.sheet_names

        target_sheet_name = "明細分類帳(依科目+部門)-0_備註欄加上承辦律師"
        if target_sheet_name not in sheet_names:
            messagebox.showwarning("錯誤", "缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
            logging.warning("缺乏名為「明細分類帳(依科目+部門)-0_備註欄加上承辦律師」的工作表(sheet)，請檢查檔案中是否有此工作表")
            return
        
        origin_sheet: DataFrame = pd.read_excel(self.selected_file_name, sheet_name=target_sheet_name)
        origin_rows: List[Tuple[object, ...]] = list(origin_sheet.itertuples(index=False, name=None))
        if not origin_rows:
            messagebox.showerror("錯誤", "工作表沒有資料，請確認檔案內容是否正確。")
            self.window.proccess_hint_text.set("格式錯誤：工作表沒有資料")
            return

        try:
            data, total_debit, total_credit = self._build_ledger_entries(origin_rows)
        except LedgerFormatError as format_err:
            messagebox.showerror("格式錯誤", format_err.message)
            self.window.proccess_hint_text.set(f"格式錯誤：{format_err.message}")
            logging.error("Ledger format error: %s", format_err.message)
            return

        try:
            target_sheet = SeparateAccountsWorksheet(output_file_name, self.window)
            target_sheet.write_data_to_worksheet(data, total_debit=total_debit, total_credit=total_credit) # 寫入分帳
            
            # 取出所有 Lawyer Code，進行遍歷
            lawyer_credits: List[dict[str, int]] = []
            lawyers = fetch_all_lawyers()
            for lawyer in lawyers:
                lawyer_total_credit = 0
                for row in data:
                    if row[5] == lawyer.code:
                        lawyer_total_credit += int(row[4])

                lawyer_credits.append({
                    "lawyer_code": lawyer.code,
                    "lawyer_total_credit": lawyer_total_credit,
                })

            logging.debug("Lawyer credit summary: %s", lawyer_credits)


            # 都沒問題，處理完畢，用 Label 告知使用者
            self.window.proccess_hint_text.set("處理完畢！")
        except LedgerFormatError as err:
            messagebox.showerror("格式錯誤", err.message)
            self.window.proccess_hint_text.set(f"格式錯誤：{err.message}")
            logging.error("寫入資料時發生格式錯誤: %s", err.message)
        except Exception as err:
            messagebox.showerror("寫入資料時發生錯誤", "請聯繫管理員！")
            logging.error(f"寫入資料到 'SeparateAccountsWorksheet' 時發生錯誤... Error: {err}")

    @staticmethod
    def _row_is_empty(row: Tuple[object, ...]) -> bool:
        return all(pd.isna(cell) or str(cell).strip() == "" for cell in row)

    def _build_ledger_entries(
        self, origin_rows: List[Tuple[object, ...]]
    ) -> Tuple[List[List[object]], int, int]:
        header_index, header_row = self._locate_header(origin_rows)

        expected_columns = {
            0: "日期",
            1: "摘要",
            2: "借方金額",
            3: "貸方金額",
            8: "部門",
            9: "備註",
        }

        mismatched_columns: List[str] = []
        for column_index, expected_value in expected_columns.items():
            raw_value = str(header_row[column_index])
            normalized_actual = self._normalize_text(raw_value)
            normalized_expected = self._normalize_text(expected_value)
            if normalized_expected not in normalized_actual:
                mismatched_columns.append(
                    f"第 {column_index + 1} 欄預期為「{expected_value}」，偵測到「{raw_value.strip() or '空白'}」"
                )

        if mismatched_columns:
            raise LedgerFormatError("；".join(mismatched_columns))

        data_rows = origin_rows[header_index + 1 :]
        if not data_rows:
            raise LedgerFormatError("表頭之後沒有資料列，請確認工作表內容。")

        data: List[List[object]] = []
        total_debit = 0
        total_credit = 0
        for offset, row in enumerate(data_rows, start=1):
            if self._row_is_empty(row):
                continue

            excel_row_number = header_index + offset + 2  # 1-based row number (+1 header row, +1 zero index)
            if len(row) < 10:
                raise LedgerFormatError(f"第 {excel_row_number} 行欄位數不足，預期至少 10 欄。")

            date = row[0]
            if pd.isna(date) or str(date).strip() == "":
                # 視為空白列，繼續尋找下一列
                continue

            abstract = str(row[1]).strip() if not pd.isna(row[1]) else ""
            debit_value = self._coerce_amount(row[2], "借方金額", excel_row_number)
            credit_value = self._coerce_amount(row[3], "貸方金額", excel_row_number)

            department_raw = row[8]
            department = str(department_raw).strip() if not pd.isna(department_raw) else ""
            if department == "" or department.lower() == "nan":
                raise LedgerFormatError(f"第 {excel_row_number} 行「部門」欄位為空白。")

            remark = str(row[9]).strip()
            if remark == "" or remark == "nan":
                raise LedgerFormatError(f"第 {excel_row_number} 行「備註」欄位缺少律師代碼。")

            lawyer_code_list = [item.strip() for item in remark.split(" ") if item.strip()]
            if not lawyer_code_list:
                raise LedgerFormatError(f"第 {excel_row_number} 行「備註」欄位缺少律師代碼。")

            insert_unique_lawyers(lawyer_code_list)

            for code in lawyer_code_list:
                separate_debit = int(round(debit_value / len(lawyer_code_list)))
                separate_credit = int(round(credit_value / len(lawyer_code_list)))
                total_debit += separate_debit
                total_credit += separate_credit

                data.append([date, abstract, department, separate_debit, separate_credit, code])

        if not data:
            raise LedgerFormatError("未能從資料中取得任何有效的律師分帳紀錄，請確認來源資料。")

        return data, total_debit, total_credit

    def _locate_header(self, origin_rows: List[Tuple[object, ...]]) -> Tuple[int, Tuple[object, ...]]:
        for index, row in enumerate(origin_rows):
            if self._row_is_empty(row):
                continue

            if len(row) < 10:
                raise LedgerFormatError(f"第 {index + 1} 行欄位數不足，預期至少 10 欄。")

            cell_value = self._normalize_text(row[9])
            if cell_value == self._normalize_text("備註"):
                return index, row

        raise LedgerFormatError("找不到包含「備註」欄位的表頭，請確認來源檔案格式。")

    @staticmethod
    def _coerce_amount(raw_value: object, column_name: str, row_number: int) -> float:
        if pd.isna(raw_value):
            return 0.0

        value_to_convert = raw_value
        if isinstance(raw_value, str):
            value_to_convert = raw_value.replace(",", "").strip()
            if value_to_convert == "":
                return 0.0

        try:
            return float(value_to_convert)
        except (TypeError, ValueError):
            raise LedgerFormatError(
                f"第 {row_number} 行「{column_name}」欄位不是有效的數字：{raw_value}"
            ) from None

    @staticmethod
    def _normalize_text(value: object) -> str:
        text = str(value).strip()
        return text.replace(" ", "").replace("\u3000", "")
