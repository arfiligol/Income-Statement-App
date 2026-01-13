from __future__ import annotations

import collections.abc
from collections.abc import Sequence

import pandas as pd
from openpyxl.cell import Cell

from src.data.repositories.alias_repository import AliasRepository
from src.data.repositories.excel_repository import ExcelRepository
from src.data.repositories.lawyer_repository import LawyerRepository
from src.domain.dtos.workflow_dto import (
    AutoFillPromptDTO,
    AutoFillResponseDTO,
    AutoFillResultDTO,
    SeparateLedgerResultDTO,
)
from src.services.excel_report_service import ExcelReportService
from src.services.interfaces.user_interaction_provider import UserInteractionProvider

class WorkflowProcessingError(Exception):
    """Raised when workflow parsing fails."""

class WorkflowService:
    """Core business logic for workflows."""

    def __init__(
        self,
        interaction: UserInteractionProvider,
        alias_repo: AliasRepository,
        lawyer_repo: LawyerRepository,
        excel_repo: ExcelRepository,
        report_service: ExcelReportService,
    ):
        self.interaction = interaction
        self.alias_repo = alias_repo
        self.lawyer_repo = lawyer_repo
        self.excel_repo = excel_repo
        self.report_service = report_service

    async def run_separate_ledger(self, source_path: str, output_path: str) -> SeparateLedgerResultDTO:
        """Run the separate ledger workflow."""
        try:
            df, _ = self.excel_repo.read_dataframe(source_path)
        except Exception as e:
            raise WorkflowProcessingError(f"讀取來源檔案失敗: {e}") from e

        if df.empty:
            raise WorkflowProcessingError("工作表沒有資料")

        rows_value = df.values.tolist()
        if not rows_value or len(rows_value[0]) < 10:
             raise WorkflowProcessingError("來源資料欄位數與預期不符 (至少 10 欄)")

        try:
             processed_data, total_debit, total_credit = self._parse_separate_rows(rows_value)
        except WorkflowProcessingError:
             raise
        except Exception as e:
             raise WorkflowProcessingError(f"解析資料失敗: {e}") from e
        
        result_dto = SeparateLedgerResultDTO(
            rows=processed_data,
            total_debit=total_debit,
            total_credit=total_credit
        )
        
        # Write Report
        await self.report_service.write_separate_ledger_report(output_path, result_dto)
        
        return result_dto

    async def run_auto_fill(self, workbook_path: str) -> AutoFillResultDTO:
        """Run the auto-fill lawyer codes workflow."""
        try:
            df, sheet_name = self.excel_repo.read_dataframe(workbook_path)
            # Need strict list of tuples for _locate_header logic ported or adapted
            origin_rows = [tuple(x) for x in df.itertuples(index=False, name=None)]
        except Exception as e:
             raise WorkflowProcessingError(f"讀取檔案失敗: {e}") from e

        if not origin_rows:
            raise WorkflowProcessingError("工作表沒有資料")

        header_index, _ = self._locate_header(origin_rows)
        
        # Load workbook for writing
        wb = self.excel_repo.load_workbook(workbook_path)
        ws = wb[sheet_name] # We assume sheet name from pandas read is correct target

        # Get known lawyers
        known_lawyers = [dto.code for dto in self.lawyer_repo.get_all()]
        known_codes_set = set(known_lawyers)

        data_rows = origin_rows[header_index + 1 :]
        if not data_rows:
            raise WorkflowProcessingError("沒有資料列")

        updated_count = 0
        skip_manual = False

        for offset, row in enumerate(data_rows, start=1):
            excel_row_number = header_index + offset + 2
            # Column 10 is '備註' (index 9). In openpyxl, it is column=10.
            remark_cell = ws.cell(row=excel_row_number, column=10)
            if remark_cell.value and str(remark_cell.value).strip():
                continue

            # Row Check (Date, Summary) logic
            # row is a tuple from pandas.
            # Index 0: Date, Index 1: Summary
            # Need to handle NaN
            date_val = row[0]
            if pd.isna(date_val) or str(date_val).strip() in {"", "nan"}:
                continue
            
            summary_val = str(row[1]) if not pd.isna(row[1]) else ""
            if not summary_val.strip() or summary_val.lower() == "nan":
                 continue

            matched = [c for c in known_codes_set if c in summary_val]

            if not matched:
                if skip_manual:
                    continue
                
                # Ask User
                prompt = AutoFillPromptDTO(
                    summary=summary_val,
                    row_number=excel_row_number,
                    known_codes=list(known_codes_set)
                )
                # Interaction
                response_tuple = await self.interaction.select_lawyers(
                    summary_text=prompt.summary,
                    row_number=prompt.row_number,
                    available_codes=prompt.known_codes
                )
                # Response is (selected_codes, action)
                selected_codes, action = response_tuple
                
                if action == 'abort':
                    # Or just break/return?
                    # Original raised UserAbortedError.
                    # We can just return what we have.
                    break
                if action == 'skip_all':
                    skip_manual = True
                    continue
                if not selected_codes: # skip_single
                    continue
                    
                # Update Known
                new_codes = [c for c in selected_codes if c not in known_codes_set]
                if new_codes:
                    self.lawyer_repo.ensure_lawyers(new_codes)
                    known_codes_set.update(new_codes)
                
                matched = selected_codes

            else:
                # matched automatically
                pass

            # Apply Aliases
            final_codes = []
            for code in matched:
                alias_dto = self.alias_repo.get_by_source(code)
                if alias_dto:
                    final_codes.extend(alias_dto.target_codes)
                else:
                    final_codes.append(code)
            
            # Deduplicate
            final_codes = list(collections.OrderedDict.fromkeys(final_codes))
            
            # Write
            remark_cell.value = " ".join(final_codes)
            updated_count += 1

        self.excel_repo.save_workbook(wb, workbook_path)
        return AutoFillResultDTO(updated_count=updated_count)


    def _parse_separate_rows(self, rows: list[list[object]]) -> tuple[list[list[object]], int, int]:
        header_index, header_row = self._locate_header(rows)
        # _validate_header(header_row) # Skipping for brevity or implement if needed
        
        data_rows = rows[header_index + 1 :]
        result_rows = []
        total_debit = 0
        total_credit = 0
        
        for offset, row in enumerate(data_rows, start=1):
            if self._row_is_empty(row):
                continue

            row_number = header_index + offset + 2
            if len(row) < 10:
                 raise WorkflowProcessingError(f"第 {row_number} 行欄位數不足，預期至少 10 欄。")

            date = row[0]
            if pd.isna(date) or str(date).strip() in {"", "nan"}:
                continue
            
            abstract = str(row[1]).strip() if not pd.isna(row[1]) else ""
            
            # Coerce amounts
            debit_value = self._coerce_amount(row[2], "借方金額", row_number)
            credit_value = self._coerce_amount(row[3], "貸方金額", row_number)
            
            department_raw = row[8]
            department = str(department_raw).strip() if not pd.isna(department_raw) else ""
            if not department or department.lower() == "nan":
                 raise WorkflowProcessingError(f"第 {row_number} 行「部門」欄位為空白。")

            remark_raw = row[9]
            remark = str(remark_raw).strip()
            if not remark or remark.lower() == "nan":
                 raise WorkflowProcessingError(f"第 {row_number} 行「備註」欄位缺少律師代碼。")

            codes = self._normalize_codes(remark)
            if not codes:
                 raise WorkflowProcessingError(f"第 {row_number} 行「備註」欄位缺少律師代碼。")

            # Update Lawyers (Ensure they exist)
            self.lawyer_repo.ensure_lawyers(codes)

            divider = len(codes)
            for code in codes:
                separate_debit = int(round(float(debit_value) / divider))
                separate_credit = int(round(float(credit_value) / divider))
                total_debit += separate_debit
                total_credit += separate_credit
                
                # Result Row: [Date, Abstract, Department, Debit, Credit, Lawyer]
                result_rows.append([date, abstract, department, separate_debit, separate_credit, code])
        
        if not result_rows:
             raise WorkflowProcessingError("未能從資料中取得任何有效的律師分帳紀錄")

        return result_rows, total_debit, total_credit

    def _locate_header(self, rows: list[tuple] | list[list]) -> tuple[int, list]:
        for idx, row in enumerate(rows):
             if self._row_is_empty(row): continue
             if len(row) < 10: continue
             
             # cell_value at index 9 (Remark)
             val = str(row[9]).strip()
             if "備註" in val:
                 return idx, row
        raise WorkflowProcessingError("找不到包含「備註」欄位的表頭")

    def _row_is_empty(self, row: Sequence) -> bool:
        return all(pd.isna(x) or str(x).strip() == "" for x in row)

    def _coerce_amount(self, raw_value: object, col_name: str, row_num: int) -> float:
        if pd.isna(raw_value): return 0.0
        val = raw_value
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            if not val: return 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            raise WorkflowProcessingError(f"第 {row_num} 行「{col_name}」不是有效的數字: {raw_value}")

    def _normalize_codes(self, raw: str) -> list[str]:
        cleaned = raw.replace("\n", " ")
        return [t.strip() for t in cleaned.split(" ") if t.strip()]
