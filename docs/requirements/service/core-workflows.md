# Core Workflows

The application primarily supports two accounting workflows for law firms.

## 1. Auto Fill Lawyer Codes (摘要抓律師代碼)
**Goal**: Populate the "Remark" (備註) column in the ledger based on the text in the "Summary" (摘要) column.

-   **Input**: An Excel file with accounting entries.
-   **Process**:
    1.  Read the file.
    2.  Scan "Summary" column for known lawyer codes (e.g., "HL", "JH").
    3.  If found, write the code into "Remark".
    4.  If not found, prompt the user to manually select or input the code (via Dialog).
        -   User can "Confirm", "Skip Single", or "Skip All" (User Abort Logic).
-   **Output**: The same Excel file, modified in-place.

## 2. Separate Ledger (律師收入明細)
**Goal**: Split shared revenue/expenses among lawyers based on the codes in the "Remark" column.

-   **Input**: An Excel file (usually processed by Auto Fill first).
-   **Target Sheet**: Looks for "明細分類帳".
-   **Process**:
    1.  Read each row.
    2.  Check "Remark" column for multiple lawyer codes (e.g., "HL JH").
    3.  Divide the Debit/Credit amounts equally by the number of lawyers.
    4.  Create new rows in the output for each lawyer with the split amount.
-   **Output**: A new Excel file containing the separated entries.
