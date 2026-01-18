from typing import Any

from income_statement_app.application.ports.gateways import UserInteractionGateway
from income_statement_app.application.ports.repositories import (
    CodeReplacementRepository,
    ExcelRepository,
    LawyerRepository,
)
from income_statement_app.common.types import Result
from income_statement_app.domain.dto.auto_fill import AutoFillPrompt, AutoFillResult
from income_statement_app.domain.dto.file_source import FileSource


class AutoFillUseCase:
    """
    Use Case: Auto-Fill Lawyer Codes
    Scans the Excel file for transactions, matches summary text against Lawyers/Aliases,
    and asks the user for input if ambiguous.
    """

    def __init__(
        self,
        excel_repo: ExcelRepository,
        lawyer_repo: LawyerRepository,
        replacement_repo: CodeReplacementRepository,
        interaction: UserInteractionGateway,
    ):
        self._excel_repo = excel_repo
        self._lawyer_repo = lawyer_repo
        self._replacement_repo = replacement_repo
        self._interaction = interaction
        self._replacement_map: dict[str, list[str]] = {}

    async def execute(self, source: FileSource) -> Result[AutoFillResult, Exception]:
        try:
            # 1. Read Raw Data
            rows_result = self._excel_repo.read_raw_rows(source)
            if not rows_result.is_success:
                return Result.failure(rows_result.error)

            rows = rows_result.value  # list[list[Any]]

            # 2. Locate Header
            header_index, header_row = self._locate_header(rows)
            # data_rows start after header
            data_rows = rows[header_index + 1 :]

            # 3. Load Knowledge Base
            known_lawyers = [l.code for l in self._lawyer_repo.get_all()]
            known_codes_set = set(known_lawyers)

            # Load Replacements
            replacements = self._replacement_repo.get_all()
            self._replacement_map = {
                r.source_code: [
                    t.strip()
                    for t in r.target_codes.replace("，", ",").split(",")
                    if t.strip()
                ]
                for r in replacements
            }

            updated_count = 0
            updates: list[tuple[int, int, str]] = []  # (row, col, value)
            skip_manual = False

            # 4. Iterate Rows
            for offset, row in enumerate(data_rows, start=1):
                excel_row_num = header_index + offset + 1

                # Check "Remark" column (Assuming col 10, index 9)
                if len(row) < 10:
                    continue

                remark_val = str(row[9]).strip()
                if remark_val and remark_val.lower() != "nan":
                    continue  # Already filled

                # Check Date/Summary
                date_val = str(row[0]).strip()
                summary_val = str(row[1]).strip()
                if not date_val or date_val.lower() == "nan":
                    continue
                if not summary_val or summary_val.lower() == "nan":
                    continue

                # Match Logic
                matched = self._find_matches(summary_val, known_codes_set)

                if not matched:
                    if skip_manual:
                        continue

                    # Ask User
                    prompt = AutoFillPrompt(
                        summary=summary_val,
                        row_number=excel_row_num,
                        available_codes=list(known_codes_set),
                    )

                    # AWAIT Interaction
                    response = await self._interaction.select_lawyers(prompt)

                    if response.action == "abort":
                        break  # Stop processing
                    if response.action == "skip_all":
                        skip_manual = True
                        continue
                    if response.action == "skip":
                        continue

                    selected_codes = response.selected_codes
                    if not selected_codes:
                        continue

                    # Learn new codes
                    new_codes = [c for c in selected_codes if c not in known_codes_set]
                    if new_codes:
                        self._lawyer_repo.ensure_exists(new_codes)
                        known_codes_set.update(new_codes)

                    # Apply Replacements
                    final_codes = self._resolve_replacements(selected_codes)
                    self._apply_updates(excel_row_num, final_codes, updates)
                    updated_count += 1
                else:
                    # Auto Matched
                    # Apply Replacements
                    final_codes = self._resolve_replacements(matched)
                    self._apply_updates(excel_row_num, final_codes, updates)
                    updated_count += 1

            # 5. Save Updates
            if updates:
                save_result = self._excel_repo.update_cells(source, updates)
                if not save_result.is_success:
                    return Result.failure(save_result.error)

            return Result.success(AutoFillResult(updated_count=updated_count))

        except Exception as e:
            return Result.failure(e)

    def _locate_header(self, rows: list[list[Any]]) -> tuple[int, list[Any]]:
        for idx, row in enumerate(rows):
            if len(row) < 10:
                continue
            val = str(row[9]).strip()  # Col 10 is Remark
            if "備註" in val:
                return idx, row
        raise Exception("Header not found (expected '備註' in column 10)")

    def _find_matches(self, summary: str, known_codes: set[str]) -> list[str]:
        # 1. Direct match with known codes
        matches = [c for c in known_codes if c in summary]
        return matches

    def _resolve_replacements(self, codes: list[str]) -> list[str]:
        final = []
        for code in codes:
            if code in self._replacement_map:
                final.extend(self._replacement_map[code])
            else:
                final.append(code)
        return final

    def _apply_updates(self, row_num: int, codes: list[str], updates: list):
        # Join unique codes
        val = " ".join(list(dict.fromkeys(codes)))
        # Update col 10 (index 10 for 1-based openpyxl)
        updates.append((row_num, 10, val))
