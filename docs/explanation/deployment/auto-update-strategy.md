# 部署與自動更新策略 (Deployment & Auto-Update Strategy)

## 概述

本文件說明 Income Statement App 採用的 **「重啟更新 (Restart to Update)」** 策略。
目標是提供無縫的更新體驗：使用者點擊「更新」按鈕，等待下載完成，應用程式自動重啟並進入新版本。

## 架構

我們使用 **PyInstaller** 進行打包，並配合自定義的 **Script Swap** 機制來執行更新。

### 1. 打包 (Packaging): PyInstaller (`nicegui-pack`)

我們使用 `nicegui-pack` (封裝了 PyInstaller) 進行發布建置。

*   **格式**: 推薦使用 `onedir` (目錄模式)，啟動速度比 `onefile` 快，且更易於進行局部更新。
*   **產出物**:
    *   **Windows**: 包含 `app.exe` 與 `_internal/` 的資料夾。
    *   **macOS**: 一個 `.app` bundle (應用程式套件)。

### 2. 更新流程 (Update Workflow)

更新流程包含四個階段：**檢查 (Check)**、**下載 (Download)**、**置換 (Swap)**、**重啟 (Restart)**。

#### 階段 1: 檢查 (Check - Business Logic)
*   **觸發**: 應用程式啟動或使用者手動點擊。
*   **動作**: 呼叫 GitHub API `GET /repos/{owner}/{repo}/releases/latest`。
*   **比對**: 將 `tag_name` 與本地 `app.common.version.__version__` 進行比對。
*   **UI**: 顯示「發現新版本」標示或按鈕。

#### 階段 2: 下載 (Download - Infrastructure)
*   **動作**: 從 GitHub Releases 下載對應平台的產物 (`windows.zip` 或 `macos.zip`)。
*   **位置**: 下載至暫存目錄 (例如使用者的 `Temp` 或 `Downloads/IncomeStatement_Update`)。
*   **解壓**: 將 ZIP 解壓至 Staging 資料夾 (例如 `.../Staging/NewVersion`)。

#### 階段 3: 置換 (Swap - The "Magic" Script)
這是最關鍵的部分，用來處理作業系統特定的限制 (Windows 的檔案鎖定)。

1.  **產生腳本**: 執行中的 App 會產生一個暫時的 Shell Script (`.sh` for macOS) 或 Batch Script (`.bat` for Windows)。
2.  **執行與退出**:
    *   App 會將腳本作為 **獨立進程 (Separate Process)** 啟動 (`subprocess.Popen`)。
    *   App **立即自行終止** (`sys.exit()`) 以釋放檔案鎖定。

**腳本的工作 (The Script's Job):**
1.  **等待**: 等待 1-2 秒，確保主程式進程已完全結束。
2.  **備份**: 將目前的安裝目錄移動到備份路徑 (例如 `OldVersion_Bak`)。
3.  **移動**: 將解壓好的 `NewVersion` 資料夾移動到原始安裝路徑。
4.  **清理**: 刪除 `OldVersion_Bak` (可選)。
5.  **重啟**: 啟動新的執行檔。

#### 階段 4: 重啟 (Restart)
腳本啟動新的執行檔，使用者看到更新後的 App 開啟。

---

## 作業系統特性與陷阱

### 🪟 Windows (關鍵)

**挑戰 1: 檔案鎖定 (File Locking)**
*   **問題**: 當進程執行中時，無法刪除或覆蓋 `app.exe` 或 DLL 檔。
*   **解法**: "Script Swap" 方法解決了此問題。腳本在 App 進程 **外部** 執行。
*   **陷阱**: 如果 App 關閉太慢，腳本可能會移動檔案失敗。
*   **緩解**: 腳本內建重試迴圈 (Retry Loop)。

**挑戰 2: UAC / 權限**
*   **問題**: 如果安裝在 `C:\Program Files`，寫入需要管理員權限。
*   **政策**: 我們假設 App 部署在使用者可寫入的位置 (桌面、Portable 資料夾、`%LOCALAPPDATA%`)。

### 🍎 macOS

**挑戰 1: Gatekeeper & Quarantine**
*   **問題**: 下載的執行檔/腳本會被標記 `com.apple.quarantine` 屬性。執行時會觸發「應用程式已損毀 (App is damaged)」或「未識別的開發者」警告。
*   **解法 (Robust)**: 正確的 Code Signing 與 Notarization (需要 Apple Developer Account)。
*   **解法 (Workaround)**: 在更新腳本中執行 `xattr -cr /path/to/extracted/App.app` 來清除 Quarantine 標記。

**挑戰 2: App Bundles**
*   **問題**: macOS App 本質上是資料夾 (`.app`)。
*   **解法**: 腳本必須確認移動的是整個 `.app` bundle，而不只是內部的執行檔。

---

## 實作變更 (Implementation Plan)

### 第一階段: 打包設定
1.  建立 `build.py` 自動化雙平台的 PyInstaller 建置。
2.  確保 `version.py` 存在且可讀取。

### 第二階段: 更新邏輯 (Backend)
1.  **UpdateManager**: `check_update()`, `download_update()`。
2.  **ScriptGenerator**: `generate_windows_updater()`, `generate_macos_updater()`。

### 第三階段: UI 整合
1.  在側邊欄顯示 `Version`。
2.  加入 `UpdateDialog` 顯示進度條。

---

## 更新腳本範例

### Windows (`updater.bat`)
```batch
@echo off
timeout /t 2 /nobreak > NUL

:RETRY_MOVE
move /Y "C:\Path\To\CurrentApp" "C:\Path\To\CurrentApp.bak"
if errorlevel 1 (
    timeout /t 1 /nobreak
    goto RETRY_MOVE
)

move /Y "C:\Path\To\NewApp" "C:\Path\To\CurrentApp"
start "" "C:\Path\To\CurrentApp\app.exe"
```

### macOS (`updater.sh`)
```bash
#!/bin/bash
sleep 2

# Path variables injected by Python
CURRENT_APP="/Applications/IncomeStatement.app"
NEW_APP="/tmp/update_stage/IncomeStatement.app"

# Remove Quarantine (Crucial for auto-update without signing)
xattr -cr "$NEW_APP"

# Swap
rm -rf "$CURRENT_APP" 
mv "$NEW_APP" "$CURRENT_APP"

# Relaunch
open "$CURRENT_APP"
```
