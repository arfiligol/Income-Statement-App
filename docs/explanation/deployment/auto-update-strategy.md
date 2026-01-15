# Deployment & Auto-Update Strategy

## Overview

This document describes the **"Restart to Update"** strategy for the Income Statement App.
The goal is to provide a seamless update experience where the user clicks "Update", waits for the download, and the application automatically restarts into the new version.

## Architecture

We utilize **PyInstaller** for packaging and a custom **Script Swap** mechanism for updates.

### 1. Packaging: PyInstaller (`nicegui-pack`)

We use `nicegui-pack` (which wraps PyInstaller) to create the distribution.
*   **Format**: `onedir` (Directory-based) is recommended over `onefile` for faster startup and easier updates.
*   **Output**:
    *   **Windows**: A folder containing `app.exe` and `_internal/`.
    *   **macOS**: A `.app` bundle (Application Bundle).

### 2. Update Workflow

The update process consists of 4 stages: **Check**, **Download**, **Swap**, **Restart**.

#### Stage 1: Check (Business Logic)
*   **Trigger**: App launch or User manual click.
*   **Action**: Call GitHub API `GET /repos/{owner}/{repo}/releases/latest`.
*   **Comparison**: Compare `tag_name` with local `app.common.version.__version__`.
*   **UI**: Show "New Version Available" badge.

#### Stage 2: Download (Infrastructure)
*   **Action**: Download the platform-specific asset (`windows.zip` or `macos.zip`) from GitHub Releases.
*   **Location**: Download to a temporary directory (e.g., user's `Temp` or `Downloads/IncomeStatement_Update`).
*   **Extraction**: Extract the ZIP file to a staging folder (e.g., `.../Staging/NewVersion`).

#### Stage 3: Swap (The "Magic" Script)
This is the most critical part, handling OS-specific constraints (File Locking on Windows).

1.  **Generate Script**: The running App generates a temporary Shell Script (`.sh` for macOS) or Batch Script (`.bat` for Windows).
2.  **Execute & Exit**:
    *   The App spawns the script as a **separate process** (`subprocess.Popen`).
    *   The App **immediately terminates itself** (`sys.exit()`) to release file locks.

**The Script's Job:**
1.  **Wait**: Sleep for 1-2 seconds to ensure the main App process has fully terminated.
2.  **Backup**: Move the current installation folder to a backup path (e.g., `OldVersion_Bak`).
3.  **Move**: Move the extracted `NewVersion` folder to the original installation path.
4.  **Cleanup**: Delete the `OldVersion_Bak` (optional, or keep for rollback).
5.  **Restart**: Lauch the new executable.

#### Stage 4: Restart
The script launches the new executable, and the user sees the updated App open up.

---

## Operating System Specifics & Pitfalls

### 🪟 Windows (Crucial)

**Challenge 1: File Locking**
*   **Issue**: You cannot delete or overwrite `app.exe` or DLLs while the process is running.
*   **Solution**: The "Script Swap" approach solves this. The script runs *outside* the App process.
*   **Pitfall**: If the App takes too long to close, the script might fail to move files.
*   **Mitigation**: The script includes a retry loop (try move, if permission denied, sleep 1s, retry).

**Challenge 2: UAC / Permissions**
*   **Issue**: If installed in `C:\Program Files`, writing requires Administrator privileges.
*   **Solution**: Recommended to install/run as a **User-space Application** (e.g., Portable Mode or strictly in `%LOCALAPPDATA%`).
*   **Policy**: We assume the App is deployed in a User-writable location (Desktop, Portable folder, etc.).

### 🍎 macOS

**Challenge 1: Gatekeeper & Quarantine**
*   **Issue**: Downloaded executable/script gets `com.apple.quarantine` attribute. Running it triggers "App is damaged" or "Unidentified Developer".
*   **Solution (Robust)**: Proper Code Signing & Notarization (Requires Apple Developer Account).
*   **Solution (Workaround)**: Run `xattr -cr /path/to/extracted/App.app` in the updater script to clear quarantine flags before launching.

**Challenge 2: App Bundles**
*   **Issue**: macOS Apps are folders (`.app`).
*   **Solution**: The script must verify it is moving the entire `.app` bundle, not just the inner executable.

---

## Implementation Plan

### Phase 1: Packaging Setup
1.  Create `build.py` to automate PyInstaller builds for both platforms.
2.  Ensure `version.py` is included and readable.

### Phase 2: Update Logic (Backend)
1.  **UpdateManager**: `check_update()`, `download_update()`.
2.  **ScriptGenerator**: `generate_windows_updater()`, `generate_macos_updater()`.

### Phase 3: UI Integration
1.  Add `Version` display in Sidebar.
2.  Add `UpdateDialog` with progress bar.

---

## Example Updater Scripts

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
