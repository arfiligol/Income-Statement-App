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

### 標準執行
```bash
uv run start
```

### Hot Reload (開發推薦)
NiceGUI 支援透過 `reload` 旗標進行熱重載。使用以下指令啟用：

```bash
NICEGUI_RELOAD=1 python main.py
```

## 打包發布 (Packaging)

專案打包由 **PyInstaller (nicegui-pack)** 處理，並整合了自動更新機制。

1.  **一鍵打包 (Build & Zip)**：
    ```bash
    python build.py
    ```

腳本會自動執行以下步驟：
- 清理 `build/` 與 `dist/` 目錄。
- 使用 `nicegui-pack` 產生執行檔。
- 將產出物壓縮為 `dist/macos.zip` 或 `dist/windows.zip`。

2.  **發布 (Release)**：
    將產生的 `.zip` 檔案上傳至 GitHub Releases。
