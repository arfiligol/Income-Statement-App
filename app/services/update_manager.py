import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import requests

from app.common.version import __version__

# Constants
GITHUB_OWNER = "arfiligol"
GITHUB_REPO = "Income-Statement-App"
GITHUB_API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)


class UpdateManager:
    def __init__(self):
        self.current_version = __version__
        self.latest_version: Optional[str] = None
        self.download_url: Optional[str] = None

    def check_for_update(self) -> Tuple[bool, Optional[str]]:
        """
        Check GitHub for the latest release.
        Returns: (has_update, latest_version_tag)
        """
        try:
            response = requests.get(GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            tag_name = data.get("tag_name", "").strip().lstrip("v")
            self.download_url = self._get_asset_url(data.get("assets", []))

            if not tag_name or not self.download_url:
                print("No valid release tag or asset found.")
                return False, None

            # Simple comparison: if tag != current, assume update.
            # (Better: use semver lib, but text comparison works if format is consistent)
            if tag_name != self.current_version:
                self.latest_version = tag_name
                return True, tag_name

            return False, None
        except Exception as e:
            print(f"Update check failed: {e}")
            return False, None

    def _get_asset_url(self, assets: list) -> Optional[str]:
        """Find platform specific asset."""
        system = platform.system().lower()
        target_name = "macos.zip" if system == "darwin" else "windows.zip"

        for asset in assets:
            if asset.get("name") == target_name:
                return asset.get("browser_download_url")
        return None

    def download_and_install(self, progress_callback=None):
        """
        Download the update, extract, and run the swap script.
        """
        if not self.download_url:
            raise ValueError("No download URL found. Run check_for_update first.")

        # 1. Download
        temp_dir = Path(tempfile.mkdtemp(prefix="IncomeStatement_Update_"))
        zip_path = temp_dir / "update.zip"

        print(f"Downloading to {zip_path}...")
        try:
            with requests.get(self.download_url, stream=True) as r:
                r.raise_for_status()
                total_length = int(r.headers.get("content-length", 0))
                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_length > 0:
                            progress_callback(downloaded / total_length)

            # 2. Extract
            print("Extracting...")
            extract_dir = temp_dir / "extracted"
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Find the inner app folder
            # For Windows: inside zip 'IncomeStatement/app.exe', so we look for 'IncomeStatement' folder
            # For macOS: inside zip 'IncomeStatement/IncomeStatement.app' or similar structure

            new_app_path = self._find_app_root(extract_dir)
            if not new_app_path:
                raise FileNotFoundError("Could not find application in update archive.")

            # 3. Generate Script & Swap
            current_app_path = self._get_current_app_path()
            print(f"Swapping {current_app_path} with {new_app_path}")

            if platform.system() == "Windows":
                self._run_windows_update(current_app_path, new_app_path, temp_dir)
            elif platform.system() == "Darwin":
                self._run_macos_update(current_app_path, new_app_path, temp_dir)

        except Exception as e:
            print(f"Update failed: {e}")
            raise e

    def _find_app_root(self, extract_dir: Path) -> Optional[Path]:
        """Find the executable folder (Windows) or .app (macOS) in extracted files."""
        # Simple heuristic: Look for folder matching APP_NAME
        # The zip structure from build.py is:
        # root/IncomeStatement/...
        target = extract_dir / "IncomeStatement"
        if target.exists():
            return target

        # Fallback: look for .app on macOS
        if platform.system() == "Darwin":
            apps = list(extract_dir.rglob("*.app"))
            if apps:
                return apps[0]

        # Fallback for Windows: look for folder containing main executable?
        return None

    def _get_current_app_path(self) -> Path:
        """Get the directory of the currently running app."""
        # When frozen (bundled), sys.executable is the .exe (Win) or binary (Mac)
        # On Windows (onedir): sys.executable is .../IncomeStatement/IncomeStatement.exe
        # On macOS (onedir): sys.executable is .../IncomeStatement.app/Contents/MacOS/IncomeStatement

        if getattr(sys, "frozen", False):
            exe_path = Path(sys.executable)
            if platform.system() == "Windows":
                # Root is the folder containing .exe
                return exe_path.parent
            elif platform.system() == "Darwin":
                # Root is the .app bundle: .../.app make sure to go up
                # .app/Contents/MacOS/Executable -> .app
                return exe_path.parents[2]
        else:
            # Development mode
            return Path(os.getcwd())

    def _run_windows_update(self, current: Path, new: Path, temp_dir: Path):
        script_path = temp_dir / "updater.bat"
        # Using ping for delay as timeout is not always robust in all shells
        script_content = f"""
@echo off
echo Waiting for application to exit...
ping 127.0.0.1 -n 3 > nul

echo Moving files...
:RETRY
move /Y "{current}" "{current}.bak"
if errorlevel 1 (
    echo File locked, retrying...
    ping 127.0.0.1 -n 2 > nul
    goto RETRY
)

move /Y "{new}" "{current}"
echo Restarting...
start "" "{current}\IncomeStatement.exe"
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        subprocess.Popen([str(script_path)], shell=True)
        sys.exit(0)

    def _run_macos_update(self, current: Path, new: Path, temp_dir: Path):
        script_path = temp_dir / "updater.sh"
        # sys.executable keeps normal path
        executable_name = "IncomeStatement"  # Guessing default name from nicegui-pack

        script_content = f"""#!/bin/bash
sleep 2
echo "Updating..."
CURRENT="{current}"
NEW="{new}"

# Clear quarantine
xattr -cr "$NEW"

# Backup
rm -rf "$CURRENT.bak"
mv "$CURRENT" "$CURRENT.bak"

# Move New
mv "$NEW" "$CURRENT"

# Restart
open "$CURRENT"
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        subprocess.Popen(["/bin/bash", str(script_path)])
        sys.exit(0)
