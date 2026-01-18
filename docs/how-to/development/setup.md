# 開發指南 (Development Guide)

## 環境設定

本專案使用 `uv` 進行套件管理。

### 安裝步驟
```bash
git clone https://github.com/arfiligol/Income-Statement-App.git
cd Income-Statement-App
uv sync
```

## 執行應用程式

### 開發模式（推薦）
```bash
uv run briefcase dev
```

### 使用 Project Script
```bash
uv run start
```

## 打包發布 (Packaging)

專案打包由 **Briefcase** 處理。

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

5.  **發布 (Release)**：
    將產生的安裝檔上傳至 GitHub Releases。

