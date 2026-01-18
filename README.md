# Income Statement App

這是一個協助律師事務所處理帳務與 Excel 明細分類帳的桌面應用程式。

## 功能特點

## 功能特點

-   **明細分帳 (Separate Ledger)**：讀取 Excel 檔案，根據備註欄位的律師代碼，自動計算並拆分借貸金額。
-   **自動填寫 (Auto Fill)**：根據摘要內容自動判斷並填入律師代碼 (Step 2)。
-   **代碼替換 (Code Replacement)**：支援設定代碼替換規則 (例如 `KW` -> `KW, HL`)，在 Step 2 自動展開多位律師。
-   **自動更新**：整合 GitHub Releases，應用程式啟動時會自動檢查並引導更新 (Restart to Update)。

## 技術架構 (Technology Stack)

本專案採用 **Clean Architecture** 與 **NiceGUI** 進行現代化重構，確保高維護性與跨平台相容性。

-   **UI Framework**: [NiceGUI](https://nicegui.io/) - 以 Python 構建 web/desktop UI。
-   **Architecture**: Clean Architecture + MVVM
    -   **Domain Layer**: DTOs (Data Transfer Objects) 定義資料結構。
    -   **Application Layer**: Use Cases + Ports 進行流程編排。
    -   **Infrastructure Layer**: Excel/DB/OS I/O 實作。
    -   **UI Layer**: ViewModel + ViewState + Effects。
-   **Core Processing**:
    -   [Pandas](https://pandas.pydata.org/): 高效能資料處理與分析。
    -   [OpenPyXL](https://openpyxl.readthedocs.io/): Excel 檔案讀寫與格式化。
-   **Database**: SQLite (透過 SQLAlchemy ORM 管理)。

## 執行應用程式

```bash
# 使用 Briefcase 開發模式（推薦）
uv run briefcase dev

# 或使用 project scripts
uv run start
```

## 安裝說明 (開發者)

本專案使用 `uv` 進行套件管理。

1.  複製專案：
    ```bash
    git clone https://github.com/arfiligol/Income-Statement-App.git
    cd Income-Statement-App
    ```

2.  安裝依賴：
    ```bash
    uv sync
    ```

3.  設定環境變數：
    ```bash
    cp .env.example .env
    ```

## 專案結構

```
Income-Statement-App/
├── src/income_statement_app/   # 主程式碼 (Briefcase src layout)
│   ├── application/            # Use Cases + Ports
│   ├── domain/                 # DTOs
│   ├── infrastructure/         # Excel/DB/OS 實作
│   ├── services/               # 服務層 (如 UpdateManager)
│   ├── ui/                     # ViewModel + Pages + Components
│   └── main.py                 # 程式進入點
├── docs/                       # 專案文件
└── pyproject.toml              # 專案設定
```

## 打包發布 (Packaging)

本專案採用 **Briefcase** 進行跨平台打包。

1.  **開發測試**：
    ```bash
    uv run briefcase dev
    ```

2.  **建立專案框架**：
    ```bash
    uv run briefcase create windows  # 或 macOS, linux
    ```

3.  **編譯執行檔**：
    ```bash
    uv run briefcase build windows
    ```

4.  **打包安裝程式**：
    ```bash
    uv run briefcase package windows
    ```

5.  **發布更新 (Release)**：
    將 `dist/` 目錄下的安裝檔上傳至 GitHub Releases，系統即可透過自動更新機制下載安裝。

## 授權 (License)

MIT License
