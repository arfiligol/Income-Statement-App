# Income Statement App

這是一個協助律師事務所處理帳務與 Excel 明細分類帳的桌面應用程式。

## 功能特點

-   **明細分帳 (Separate Ledger)**：讀取 Excel 檔案，根據備註欄位的律師代碼，自動計算並拆分借貸金額。
-   **自動填寫 (Auto Fill)**：根據摘要內容自動判斷並填入律師代碼，支援模糊比對與手動選擇。
-   **自動更新**：整合 GitHub Releases，應用程式啟動時會自動檢查並下載最新版本。

## 技術架構 (Technology Stack)

本專案採用 **Clean Architecture** 與 **Flet** 進行現代化重構，確保高維護性與跨平台相容性。

-   **UI Framework**: [Flet](https://flet.dev/) (基於 Flutter 的 Python 框架) - 提供流暢且反應迅速的 Material Design 3 使用者介面。
-   **Architecture**: Scaleable / Clean Architecture
    -   **Domain Layer**: DTOs (Data Transfer Objects) 定義資料結構。
    -   **Data Layer**: Repository Pattern (SQLAlchemy, Excel) 負責資料存取與抽象化。
    -   **UI Layer**: MVVM-like State Management (State + Logic 分離)。
-   **Core Processing**:
    -   [Pandas](https://pandas.pydata.org/): 高效能資料處理與分析。
    -   [OpenPyXL](https://openpyxl.readthedocs.io/): Excel 檔案讀寫與格式化。
-   **Database**: SQLite (透過 SQLAlchemy ORM 管理)。
-   **Packaging**: [Briefcase](https://beeware.org/project/projects/tools/briefcase/) (跨平台打包工具)。

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

## 執行應用程式

```bash
uv run start
```

## 開發模式 (Hot Reload)

Flet 支援 Hot Reload，在修改程式碼後會自動重整應用程式，適合開發時使用。

```bash
# 執行並監聽變更 (預設遞迴監聽目前的目錄)
uv run flet run src/app.py
```

## 打包發布 (Packaging)

本專案採用 **Briefcase** 進行跨平台打包。

1.  **建立專案骨架 (Create)**：
    ```bash
    uv run briefcase create
    ```

2.  **建置應用程式 (Build)**：
    ```bash
    uv run briefcase build
    ```

3.  **打包安裝檔 (Package)**：
    ```bash
    uv run briefcase package
    ```

打包完成後的安裝檔或執行檔將位於 `build/` 目錄中對應的平台資料夾內（例如 `build/Income-Statement-App/windows/app` 或 `build/Income-Statement-App/macos/app`）。

## 授權 (License)

MIT License
