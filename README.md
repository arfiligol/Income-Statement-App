# Income Statement App

這是一個協助律師事務所處理帳務與 Excel 明細分類帳的桌面應用程式。

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
# 開發模式（推薦）
uv run python src/main.py

# 或使用 project scripts (需配置後使用)
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
├── src/                        # 主程式碼
│   ├── application/            # Use Cases + Ports
│   ├── domain/                 # DTOs
│   ├── infrastructure/         # Excel/DB/OS 實作
│   ├── services/               # 服務層 (如 UpdateManager)
│   ├── ui/                     # ViewModel + Pages + Components
│   ├── static/                 # 靜態資源 (圖標等)
│   └── main.py                 # 程式進入點
├── data/                       # 開發用資料庫目錄
├── docs/                       # 專案文件
└── pyproject.toml              # 專案設定
```

## 打包發布 (Packaging)

本專案使用 **nicegui-pack** (基於 PyInstaller) 進行桌面應用打包。

### 開發測試

```bash
uv run python src/main.py
```

### 打包發布腳本 (推薦)

我們提供了一個 Python 腳本，自動完成「清理 -> 打包 -> 壓縮」的流程。

```bash
uv run python build.py
```

執行成功後，您會在 `dist/` 目錄下看到 `Income-Statement-App_platform_vX.X.X.zip` (例如 `Income-Statement-App_windows_0.2.1.zip`)。只要將此檔案上傳至 GitHub Releases 即可。

### 手動打包指令

如果您需要手動調整參數，可以使用以下指令：

**PowerShell (Windows)**
```powershell
uv run nicegui-pack `
    --name "Income-Statement-App" `
    --icon "src/static/mom_accounting.ico" `
    --onedir `
    --windowed `
    --noconfirm `
    --add-data "src/ui/styles;ui/styles" `
    --add-data "src/static;static" `
    src/main.py
```

**Bash (Git Bash / WSL)**
```bash
uv run nicegui-pack \
    --name "Income-Statement-App" \
    --icon "src/static/mom_accounting.ico" \
    --onedir \
    --windowed \
    --noconfirm \
    --add-data "src/ui/styles;ui/styles" \
    --add-data "src/static;static" \
    src/main.py
```

### 打包選項說明

| 選項 | 說明 |
|------|------|
| `--name` | 可執行檔名稱 |
| `--icon` | 應用程式圖標 (.ico) |
| `--onedir` | 輸出目錄形式（啟動較快），便於分發 |
| `--windowed` | 隱藏 console 視窗（需配合 `native=True`） |
| `--add-data` | **必要** - 包含靜態資源（CSS 樣式、圖標等） |
| `--noconfirm` | 自動覆蓋現有輸出目錄 |

### 發布更新

1. 打包完成後，`dist/Income-Statement-App/` 目錄即為可執行程式
2. 壓縮該目錄為 `.zip` 並上傳至 GitHub Releases
3. 應用程式啟動時會自動檢查更新並引導安裝

---

## 打包常見問題 (Troubleshooting)

### ❌ Briefcase 打包失敗

**問題**：之前嘗試使用 Briefcase 打包 NiceGUI native 應用，視窗無法正常顯示。

**原因**：
1. NiceGUI native 模式使用 `multiprocessing` 啟動 pywebview 進程
2. Windows 打包環境需要 `multiprocessing.freeze_support()` 在程式最開頭呼叫
3. 即使加入 freeze_support 仍有其他相容性問題

**解決方案**：改用 **nicegui-pack** (PyInstaller)。

---

### ❌ UI 樣式跑掉 (CSS 未載入)

**問題**：打包後應用程式可運行，但 UI 樣式不正確。

**原因**：PyInstaller 預設不會包含 Python 程式碼以外的資源檔案。

**解決方案**：使用 `--add-data` 參數明確指定靜態資源：
```bash
--add-data "src/ui/styles;ui/styles"
--add-data "src/static;static"
```

---

### ❌ 其他電腦無法運行

**問題**：開發機可以運行，但其他電腦無法執行。

**可能原因與解決**：
1. **缺少 VC++ Runtime** - 確保目標電腦安裝 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. **WebView2 未安裝** - NiceGUI native 模式需要 [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)
3. **Python 版本不符** - 確保使用相同 Python 版本打包

---

### ⚠️ 資料庫位置
- **開發模式**：`./data/sqlite_db.db`
- **打包後 (Portable Mode)**：`./sqlite_db.db` (與 .exe 同目錄)

---

### 👻 只有背景程序但無視窗 (Phantom Process)

**問題**：應用程式啟動後，工作管理員有看到程序，但沒有視窗跳出。

**解決方案**：
1. **檢查 Log**：查看 `%LOCALAPPDATA%\Income-Statement-App\logs\startup.log`。
2. **安裝 WebView2**：確保目標電腦已安裝 [WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)。
3. **管理員權限**：嘗試以「系統管理員身分執行」，這通常能解決 `pywebview` 寫入暫存檔的權限問題。
4. **硬體加速問題**：本版本 (v0.2.0+) 已預設停用 WebView2 硬體加速 (`--disable-gpu`) 以提升相容性。
5. **防毒軟體**：檢查是否被防毒軟體 (如 SentinelOne, CrowdStrike) 靜默封鎖。

---

### 🔒 Windows 11 DLL 被封鎖 (RuntimeError: Failed to resolve)

**問題**：應用程式啟動後出現類似以下錯誤：
```
Process Process-1:
Traceback (most recent call last):
  File "multiprocessing\process.py", line 313, in _bootstrap
  File "multiprocessing\process.py", line 108, in run
  File "nicegui\native\native_mode.py", line 50, in _open_window
  ...
  File "clr_loader\netfx.py", line 49, in _get_callable
RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize from ...\pythonnet\runtime\Python.Runtime.dll
```

或者應用程式只有背景程序但沒有視窗 (工作管理員顯示 2 個程序但無 UI)。

**原因**：Windows 11 的「網路標記」(Mark of the Web) 安全機制會自動封鎖從網路下載的 `.dll` 檔案，導致應用程式無法載入必要的動態連結庫。

**解決方案**：

**方法一：使用 PowerShell 批量解除封鎖（推薦）**

以「系統管理員身分」開啟 PowerShell，執行以下指令：

```powershell
Get-ChildItem -Path "C:\你的下載路徑\Income-Statement-App" -Recurse | Unblock-File
```

> ⚠️ 請將 `C:\你的下載路徑\Income-Statement-App` 替換為實際的應用程式路徑。

**方法二：手動解除封鎖**

1. 在檔案總管中找到 `Income-Statement-App` 資料夾
2. 進入 `_internal\pythonnet\runtime\` 目錄
3. 右鍵點擊 `Python.Runtime.dll` → **內容**
4. 在「一般」標籤最下方勾選 **「解除封鎖」**
5. 點擊 **確定**

## 授權 (License)

MIT License
