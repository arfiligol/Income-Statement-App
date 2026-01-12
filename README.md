# Income Statement App

這是一個協助律師事務所處理帳務與 Excel 明細分類帳的桌面應用程式。

## 功能特點

-   **明細分帳 (Separate Ledger)**：讀取 Excel 檔案，根據備註欄位的律師代碼，自動計算並拆分借貸金額。
-   **自動填寫 (Auto Fill)**：根據摘要內容自動判斷並填入律師代碼，支援模糊比對與手動選擇。
-   **自動更新**：整合 GitHub Releases，應用程式啟動時會自動檢查並下載最新版本。

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
