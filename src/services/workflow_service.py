from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

import unicodedata

import pandas as pd
from openpyxl import load_workbook

from src.services.dao.lawyer_dao import (
    ensure_lawyers as _ensure_lawyers,
    get_lawyers as _get_lawyers,
)


class WorkflowProcessingError(Exception):
    """Raised when workflow parsing fails."""


WORKFLOW_TARGET_SHEET = "明細分類帳(依科目+部門)-0_備註欄加上承辦律師"


@dataclass(frozen=True)
class SeparateLedgerResult:
    """Result payload for the separate-the-ledger workflow."""

    rows: List[List[object]]
    total_debit: int
    total_credit: int


@dataclass(frozen=True)
class AutoFillPrompt:
    summary: str
    row_number: int
    known_codes: List[str]


@dataclass(frozen=True)
class AutoFillResponse:
    selected_codes: List[str]
    skip_remaining: bool = False


@dataclass(frozen=True)
class AutoFillResult:
    updated_count: int


PromptHandler = Callable[[AutoFillPrompt], Optional[AutoFillResponse]]


def build_separate_ledger(source_path: str) -> SeparateLedgerResult:
    """Parse the source workbook and produce the separated ledger rows."""

    read_engine = _get_excel_read_engine(source_path)
    try:
        xls = pd.ExcelFile(source_path, engine=read_engine)
    except FileNotFoundError as err:  # pragma: no cover - handled at caller level
        raise WorkflowProcessingError("找不到來源檔案，請確認路徑是否正確。") from err
    except Exception as err:  # pragma: no cover - engine / parsing errors
        raise WorkflowProcessingError("無法開啟來源檔案，請確認檔案格式是否正確。") from err

    sheet_name = _resolve_target_sheet_name(xls.sheet_names)

    try:
        origin_sheet = xls.parse(sheet_name=sheet_name)
    except Exception as err:  # pragma: no cover - pandas specific errors
        raise WorkflowProcessingError("無法讀取目標工作表，請確認工作表內容是否正確。") from err

    origin_array = origin_sheet.values
    if origin_array.size == 0:
        raise WorkflowProcessingError("工作表沒有資料，請確認檔案內容是否正確。")
    if len(origin_array[0]) != 10:
        raise WorkflowProcessingError("來源資料欄位數與預期不符，請確認工作表格式。")

    rows, total_debit, total_credit = parse_separate_rows(origin_array, register_lawyers)
    return SeparateLedgerResult(rows=rows, total_debit=total_debit, total_credit=total_credit)


def auto_fill_lawyer_codes(
    workbook_path: str,
    *,
    prompt_handler: PromptHandler,
) -> AutoFillResult:
    read_engine = _get_excel_read_engine(workbook_path)

    try:
        xls = pd.ExcelFile(workbook_path, engine=read_engine)
    except FileNotFoundError as err:
        raise WorkflowProcessingError("找不到來源檔案，請確認路徑是否正確。") from err
    except Exception as err:
        raise WorkflowProcessingError("無法讀取目標工作表，請確認檔案是否損壞或被其他程式使用。") from err

    sheet_name = _resolve_target_sheet_name(xls.sheet_names)

    origin_sheet = xls.parse(sheet_name=sheet_name)
    origin_rows: List[Tuple[object, ...]] = list(origin_sheet.itertuples(index=False, name=None))
    if not origin_rows:
        raise WorkflowProcessingError("工作表沒有資料，請確認檔案內容是否正確。")

    header_index, _ = _locate_header(origin_rows)

    known_codes = fetch_known_lawyers()

    try:
        workbook = load_workbook(workbook_path)
    except FileNotFoundError as err:
        raise WorkflowProcessingError("找不到來源檔案，請確認路徑是否正確。") from err
    except Exception as err:  # pragma: no cover - openpyxl specific errors
        raise WorkflowProcessingError("無法開啟來源檔案進行寫入，請確認檔案是否被其他程式使用。") from err

    worksheet_name = _resolve_target_sheet_name(workbook.sheetnames)
    worksheet = workbook[worksheet_name]
    data_rows = origin_rows[header_index + 1 :]
    if not data_rows:
        raise WorkflowProcessingError("表頭之後沒有資料列，無需填入律師代碼。")

    updated_count = 0
    skip_manual_prompts = False

    for offset, row in enumerate(data_rows, start=1):
        excel_row_number = header_index + offset + 2
        remark_cell = worksheet.cell(row=excel_row_number, column=10)
        remark_value = str(remark_cell.value).strip() if remark_cell.value is not None else ""
        if remark_value:
            continue

        date_value = row[0]
        if pd.isna(date_value) or str(date_value).strip() in {"", "nan"}:
            continue

        summary_text = str(row[1]) if row[1] is not None else ""
        if summary_text.strip() == "" or summary_text.lower() == "nan":
            continue

        matched_codes = _match_codes_in_summary(summary_text, known_codes)

        if not matched_codes:
            if skip_manual_prompts:
                continue

            prompt = AutoFillPrompt(
                summary=summary_text,
                row_number=excel_row_number,
                known_codes=list(known_codes),
            )
            response = prompt_handler(prompt)
            if response is None:
                continue

            selected_codes = [code.strip() for code in response.selected_codes if code.strip()]
            if not selected_codes:
                if response.skip_remaining:
                    skip_manual_prompts = True
                continue

            register_lawyers(selected_codes)
            known_codes = sorted(set(known_codes + selected_codes))
            matched_codes = selected_codes

            if response.skip_remaining:
                skip_manual_prompts = True
        else:
            register_lawyers(matched_codes)

        remark_cell.value = " ".join(_deduplicate_preserve_order(matched_codes))
        updated_count += 1

    workbook.save(workbook_path)

    return AutoFillResult(updated_count=updated_count)


def parse_separate_rows(
    origin_array: Sequence[Sequence[object]],
    register_codes: Callable[[Iterable[str]], None],
) -> Tuple[List[List[object]], int, int]:
    header_index, header_row = _locate_header(origin_array)
    _validate_header(header_row)

    data_rows = origin_array[header_index + 1 :]
    if len(data_rows) == 0:
        raise WorkflowProcessingError("表頭之後沒有資料列，請確認來源工作表內容。")

    data: List[List[object]] = []
    total_debit = 0
    total_credit = 0

    for offset, row in enumerate(data_rows, start=1):
        if _row_is_empty(row):
            continue

        row_number = header_index + offset + 2
        if len(row) < 10:
            raise WorkflowProcessingError(f"第 {row_number} 行欄位數不足，預期至少 10 欄。")

        date = row[0]
        if pd.isna(date) or str(date).strip() == "" or str(date).lower() == "nan":
            continue

        abstract = str(row[1]).strip() if not pd.isna(row[1]) else ""
        debit_value = _coerce_amount(row[2], "借方金額", row_number)
        credit_value = _coerce_amount(row[3], "貸方金額", row_number)

        department_raw = row[8]
        department = str(department_raw).strip() if not pd.isna(department_raw) else ""
        if department == "" or department.lower() == "nan":
            raise WorkflowProcessingError(f"第 {row_number} 行「部門」欄位為空白。")

        remark_raw = row[9]
        remark = str(remark_raw).strip()
        if remark == "" or remark.lower() == "nan":
            raise WorkflowProcessingError(f"第 {row_number} 行「備註」欄位缺少律師代碼。")

        codes = _normalize_codes(remark)
        if not codes:
            raise WorkflowProcessingError(f"第 {row_number} 行「備註」欄位缺少律師代碼。")

        register_codes(codes)

        divider = len(codes)
        for code in codes:
            separate_debit = int(round(float(debit_value) / divider))
            separate_credit = int(round(float(credit_value) / divider))
            total_debit += separate_debit
            total_credit += separate_credit
            data.append([date, abstract, department, separate_debit, separate_credit, code])

    if not data:
        raise WorkflowProcessingError("未能從資料中取得任何有效的律師分帳紀錄，請確認來源資料。")

    return data, total_debit, total_credit


def _normalize_codes(raw: str) -> List[str]:
    cleaned = raw.replace("\n", " ")
    return [token for token in (piece.strip() for piece in cleaned.split(" ")) if token]


def fetch_known_lawyers() -> List[str]:
    return [lawyer.code for lawyer in _get_lawyers()]


def register_lawyers(codes: Iterable[str]) -> None:
    _ensure_lawyers(codes)


def get_filename_validator() -> Callable[[str], bool]:
    from src.utils.validation import filename_has_invalid_chars

    return filename_has_invalid_chars


def _get_excel_read_engine(file_path: str) -> str:
    return "xlrd" if file_path.lower().endswith(".xls") else "openpyxl"


def _locate_header(origin_rows: Sequence[Sequence[object]]) -> Tuple[int, Sequence[object]]:
    for index, row in enumerate(origin_rows):
        if _row_is_empty(row):
            continue

        if len(row) < 10:
            raise WorkflowProcessingError(f"第 {index + 1} 行欄位數不足，預期至少 10 欄。")

        cell_value = _normalize_text(row[9])
        if cell_value == _normalize_text("備註"):
            return index, row

    raise WorkflowProcessingError("找不到包含「備註」欄位的表頭，請確認來源檔案格式。")


def _validate_header(header_row: Sequence[object]) -> None:
    expected_columns = {
        0: "日期",
        1: "摘要",
        2: "借方金額",
        3: "貸方金額",
        8: "部門",
        9: "備註",
    }

    mismatched: List[str] = []
    for column_index, expected_value in expected_columns.items():
        if column_index >= len(header_row):
            mismatched.append(f"第 {column_index + 1} 欄預期為「{expected_value}」，偵測到「空白」。")
            continue

        raw_value = str(header_row[column_index])
        normalized_actual = _normalize_text(raw_value)
        normalized_expected = _normalize_text(expected_value)
        if normalized_expected not in normalized_actual:
            display_value = raw_value.strip() or "空白"
            mismatched.append(
                f"第 {column_index + 1} 欄預期為「{expected_value}」，偵測到「{display_value}」"
            )

    if mismatched:
        raise WorkflowProcessingError("；".join(mismatched))


def _row_is_empty(row: Sequence[object]) -> bool:
    return all(pd.isna(cell) or str(cell).strip() == "" for cell in row)


def _coerce_amount(raw_value: Any, column_name: str, row_number: int) -> float:
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
        raise WorkflowProcessingError(
            f"第 {row_number} 行「{column_name}」欄位不是有效的數字：{raw_value}"
        ) from None


def _normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = text.replace(" ", "").replace("\u3000", "")
    text = "".join(ch for ch in text if not ch.isspace())
    return text.lower()


def _resolve_target_sheet_name(sheet_names: Sequence[str]) -> str:
    if WORKFLOW_TARGET_SHEET in sheet_names:
        return WORKFLOW_TARGET_SHEET

    normalized_target = _normalize_text(WORKFLOW_TARGET_SHEET)

    def normalized(name: str) -> str:
        return _normalize_text(name)

    for name in sheet_names:
        candidate = normalized(name)
        if candidate == normalized_target:
            return name

    for name in sheet_names:
        candidate = normalized(name)
        if normalized_target in candidate or candidate in normalized_target:
            return name

    available = "\n".join(f"- {name}" for name in sheet_names) or "<無任何工作表>"
    raise WorkflowProcessingError(
        "找不到預期的律師備註工作表，請確認來源檔案是否包含『"
        f"{WORKFLOW_TARGET_SHEET}』，或檢查工作表名稱（目前偵測到：\n{available}）"
    )


def _match_codes_in_summary(summary: str, available_codes: Sequence[str]) -> List[str]:
    normalized_summary = summary
    matched: List[str] = []
    for code in available_codes:
        if code and code in normalized_summary:
            matched.append(code)
    return matched


def _deduplicate_preserve_order(codes: Sequence[str]) -> List[str]:
    seen = set()
    ordered_codes: List[str] = []
    for code in codes:
        normalized = code.strip()
        if not normalized:
            continue
        if normalized not in seen:
            seen.add(normalized)
            ordered_codes.append(normalized)
    return ordered_codes
