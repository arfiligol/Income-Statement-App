import os
import secrets
from typing import List

from app.application.ports.gateways import ReportGateway
from app.application.ports.repositories import ExcelRepository, LawyerRepository
from app.common.errors import ValidationError
from app.common.types import Result
from app.domain.dto.file_source import FileSource
from app.domain.dto.separate_ledger import SeparateLedgerResult, SeparateLedgerRow


class SeparateLedgerUseCase:
    """
    Use Case: Generate Separate Ledger
    Parses Auto-Filled Excel, splits shared transactions, and generates a report.
    """

    def __init__(
        self,
        excel_repo: ExcelRepository,
        lawyer_repo: LawyerRepository,
        report_gateway: ReportGateway,
    ):
        self._excel_repo = excel_repo
        self._lawyer_repo = lawyer_repo
        self._report_gateway = report_gateway

    def execute(self, source: FileSource) -> Result[SeparateLedgerResult, Exception]:
        try:
            # 1. Read Raw Data
            rows_res = self._excel_repo.read_raw_rows(source)
            if not rows_res.is_success:
                return Result.failure(rows_res.error)

            rows = rows_res.value

            # 2. Locate Header & Filter Rows
            header_index = self._locate_header_index(rows)
            data_rows = rows[header_index + 1 :]

            result_rows: list[SeparateLedgerRow] = []
            total_debit = 0
            total_credit = 0

            # 3. Process Rows
            for offset, row in enumerate(data_rows, start=1):
                raw_row = row
                # Validation
                if len(raw_row) < 10:
                    continue
                # Date check
                date_val = str(raw_row[0]).strip()
                if not date_val or date_val.lower() == "nan":
                    continue

                abstract = str(raw_row[1]).strip()
                department = str(raw_row[8]).strip()  # Col 9 is Dept
                if department.lower() == "nan":
                    department = ""

                # Remark (Lawyer Codes)
                remark = str(raw_row[9]).strip()
                if not remark or remark.lower() == "nan":
                    # Skip or Error? Original logic raised error or skipped.
                    # We skip for now unless strict mode.
                    continue

                codes = [c.strip() for c in remark.split(" ") if c.strip()]
                if not codes:
                    continue

                # Amounts (Cols 3 & 4 -> Index 2 & 3)
                try:
                    debit = float(str(raw_row[2]).replace(",", "") or 0)
                    credit = float(str(raw_row[3]).replace(",", "") or 0)
                except ValueError:
                    continue  # Skip invalid amount rows

                # Split Logic
                count = len(codes)
                split_debit = int(round(debit / count))
                split_credit = int(round(credit / count))

                for code in codes:
                    # Create Row per Lawyer
                    result_rows.append(
                        SeparateLedgerRow(
                            date=date_val,
                            abstract=abstract,
                            department=department,
                            debit=split_debit,
                            credit=split_credit,
                            lawyer_code=code,
                        )
                    )
                    total_debit += split_debit
                    total_credit += split_credit

            if not result_rows:
                return Result.failure(
                    ValidationError("No valid ledger rows generated.")
                )

            # 4. Generate Output Report
            # Generate path: same dir as source, different name
            src_path = str(source.path) if source.path else "report.xlsx"
            dir_name = os.path.dirname(src_path)
            base_name = os.path.splitext(os.path.basename(src_path))[0]
            # Suffix with timestamp or '_separate'
            out_path = os.path.join(dir_name, f"{base_name}_separate_ledger.xlsx")

            result_dto = SeparateLedgerResult(
                rows=result_rows,
                total_debit=total_debit,
                total_credit=total_credit,
                output_path=out_path,
            )

            report_res = self._report_gateway.generate_ledger_report(
                result_dto, out_path
            )
            if not report_res.is_success:
                return Result.failure(report_res.error)

            return Result.success(result_dto)

        except Exception as e:
            return Result.failure(e)

    def _locate_header_index(self, rows: list[list]) -> int:
        for idx, row in enumerate(rows):
            if len(row) < 10:
                continue
            if "備註" in str(row[9]):
                return idx
        # Default fallback if not found? Or raise error.
        # Original logic raised error.
        raise ValidationError("Header row not found.")
