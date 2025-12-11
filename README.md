# Mom Work Project

這是一個協助律師事務所處理帳務與 Excel 明細分類帳的桌面應用程式。

## 功能特點

-   **明細分帳 (Separate Ledger)**：讀取 Excel 檔案，根據備註欄位的律師代碼，自動計算並拆分借貸金額。
-   **自動填寫 (Auto Fill)**：根據摘要內容自動判斷並填入律師代碼，支援模糊比對與手動選擇。
-   **自動更新**：整合 GitHub Releases，應用程式啟動時會自動檢查並下載最新版本。

## 安裝說明 (開發者)

本專案使用 `uv` 進行套件管理。

1.  複製專案：
    ```bash
    git clone https://github.com/arfiligol/mom-work-project.git
    cd mom-work-project
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

## 打包發布

使用 PyInstaller 打包成單一執行檔：

```bash
uv run pyinstaller build.spec
```

執行後，可在 `dist/` 資料夾中找到 `mom-work-project.exe`。

## 授權 (License)

MIT License
