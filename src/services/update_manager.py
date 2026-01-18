import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from common.version import __version__

# Constants
GITHUB_OWNER = "arfiligol"
GITHUB_REPO = "Income-Statement-App"
GITHUB_API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)


class UpdateManager:
    def __init__(self):
        self.current_version = __version__
        self.latest_version: str | None = None
        self.download_url: str | None = None

    def check_for_update(self) -> tuple[bool, str | None]:
        """
        Check GitHub for the latest release.
        Returns: (has_update, latest_version_tag)
        """
        try:
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session = requests.Session()
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            response = session.get(GITHUB_API_URL, timeout=15)
            response.raise_for_status()
            data = response.json()

            tag_name = data.get("tag_name", "").strip().lstrip("v")
            assets = data.get("assets", [])
            print(f"DEBUG: Found tag: {tag_name}")
            print(f"DEBUG: Available assets: {[a.get('name') for a in assets]}")

            self.download_url = self._get_asset_url(assets)

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

    def _get_asset_url(self, assets: list) -> str | None:
        """Find platform specific asset."""
        system = platform.system().lower()
        # Look for "windows" or "macos/darwin" in the name, and must be .zip
        target_os = "macos" if system == "darwin" else "windows"

        for asset in assets:
            name = asset.get("name", "").lower()
            if target_os in name and name.endswith(".zip"):
                return asset.get("browser_download_url")
        return None

    def download_and_install(self, progress_callback=None):
        """
        Download the update, extract, and run the swap script.
        """
        if not self.download_url:
            raise ValueError("No download URL found. Run check_for_update first.")

        # Check dev mode
        is_dev = not getattr(sys, "frozen", False)

        # 1. Download
        temp_dir = Path(tempfile.mkdtemp(prefix="IncomeStatement_Update_"))
        zip_path = temp_dir / "update.zip"

        print(f"Downloading to {zip_path}...")
        try:
            with requests.get(self.download_url, stream=True) as r:
                r.raise_for_status()
                total_length = int(r.headers.get("content-length", 0))
                print(f"DEBUG: Download size: {total_length} bytes")

                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            if total_length > 0:
                                progress_callback(downloaded / total_length)
                            else:
                                # Fallback if no length provided: indeterminate or fake progress
                                # Just show something moving? Or keep at 0?
                                pass

            # 2. Extract
            print("Extracting...")
            extract_dir = temp_dir / "extracted"
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Find the inner app folder
            new_app_path = self._find_app_root(extract_dir)
            if not new_app_path:
                raise FileNotFoundError("Could not find application in update archive.")

            # SAFETY CHECK: Stop here in dev mode
            if is_dev:
                print("DEV MODE: Download and extract successful.")
                print(f"Update ready at: {new_app_path}")
                print("Skipping file swap and restart to protect source code.")
                if progress_callback:
                    progress_callback(1.0)
                return

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

    def _find_app_root(self, extract_dir: Path) -> Path | None:
        """Find the executable folder (Windows) or .app (macOS) in extracted files."""
        # Simple heuristic: Look for folder matching APP_NAME
        # The zip structure from build.py is:
        # root/Income-Statement-App/...
        target = extract_dir / "Income-Statement-App"
        if target.exists():
            return target

        # Fallback: look for .app on macOS
        if platform.system() == "Darwin":
            apps = list(extract_dir.rglob("*.app"))
            if apps:
                return apps[0]

        # Fallback for Windows: check for subfolder containing main exe
        if platform.system() == "Windows":
            # Sometimes extract might add an extra level
            # Recurse one or two levels? Or just assume one level.
            for item in extract_dir.iterdir():
                if item.is_dir() and (item / "Income-Statement-App.exe").exists():
                    return item

        # Fallback: look for folder containing main executable?
        return None

    def _get_current_app_path(self) -> Path:
        """Get the directory of the currently running app."""
        # When frozen (bundled), sys.executable is the .exe (Win) or binary (Mac)
        # On Windows (onedir): sys.executable is .../Income-Statement-App/Income-Statement-App.exe
        # On macOS (onedir): sys.executable is .../Income-Statement-App.app/Contents/MacOS/Income-Statement-App

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
        script_content = rf"""
@echo off
echo Waiting for application to exit...
timeout /t 3 /nobreak > nul

:: Force kill just in case (Kill Tree)
taskkill /F /T /IM Income-Statement-App.exe > nul 2>&1

echo Moving files...
:RETRY
:: Try to rename the current folder to backup
move /Y "{current}" "{current}.bak"
if errorlevel 1 (
    echo File locked, retrying...
    timeout /t 2 /nobreak > nul
    taskkill /F /T /IM Income-Statement-App.exe > nul 2>&1
    goto RETRY
)

:: Move the new folder to current location
move /Y "{new}" "{current}"
if errorlevel 1 (
    echo Move failed, restoring backup...
    move /Y "{current}.bak" "{current}"
    pause
    exit
)

echo Restarting...
start "" "{current}\Income-Statement-App.exe"
"""
        with open(script_path, "w") as f:
            f.write(script_content)

        # Run with CWD set to temp_dir to avoid locking the application directory
        subprocess.Popen([str(script_path)], shell=True, cwd=str(temp_dir))
        os._exit(0)

    def _run_macos_update(self, current: Path, new: Path, temp_dir: Path):
        script_path = temp_dir / "updater.sh"
        # sys.executable keeps normal path
        executable_name = (
            "Income-Statement-App"  # Guessing default name from nicegui-pack
        )

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
        os._exit(0)
