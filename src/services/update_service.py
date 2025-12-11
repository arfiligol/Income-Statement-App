import logging
import os
import sys
import subprocess
import shutil
import tempfile
import time
from dataclasses import dataclass
from typing import Optional
import requests
from threading import Thread

logger = logging.getLogger(__name__)

REPO_OWNER = "arfiligol"
REPO_NAME = "mom-work-project"
GITHUB_API_URL = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
)


@dataclass
class UpdateInfo:
    version: str
    download_url: str
    release_notes: str


class UpdateService:
    def __init__(self, current_version: str):
        self.current_version = current_version
        self._available_update: Optional[UpdateInfo] = None
        self._temp_dir = tempfile.mkdtemp(prefix="mom_update_")

    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check GitHub for the latest release."""
        try:
            logging.info("Checking for updates from %s...", GITHUB_API_URL)
            response = requests.get(GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version = data["tag_name"].lstrip("v")
            if latest_version == self.current_version:
                logging.info("App is up to date (version %s).", self.current_version)
                return None

            # Find the executable asset
            exe_asset = next(
                (asset for asset in data["assets"] if asset["name"].endswith(".exe")),
                None,
            )

            if not exe_asset:
                logging.warning(
                    "New release found (%s) but no .exe asset.", latest_version
                )
                return None

            update_info = UpdateInfo(
                version=latest_version,
                download_url=exe_asset["browser_download_url"],
                release_notes=data["body"],
            )
            self._available_update = update_info
            logging.info(
                "Update available: %s -> %s", self.current_version, latest_version
            )
            return update_info

        except Exception as e:
            logging.error("Failed to check for updates: %s", e)
            return None

    def get_available_update(self) -> Optional[UpdateInfo]:
        return self._available_update

    def perform_update(self, update_info: UpdateInfo) -> None:
        """Download and install the update in a background thread."""
        thread = Thread(target=self._download_and_install, args=(update_info,))
        thread.start()

    def _download_and_install(self, update_info: UpdateInfo) -> None:
        try:
            download_path = os.path.join(self._temp_dir, "new_version.exe")
            logging.info("Downloading update from %s...", update_info.download_url)

            with requests.get(update_info.download_url, stream=True) as r:
                r.raise_for_status()
                with open(download_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            logging.info("Download completed. Preparing to restart...")
            self._restart_and_replace(download_path)

        except Exception as e:
            logging.error("Update failed: %s", e)

    def _restart_and_replace(self, new_exe_path: str) -> None:
        """Create a batch script to replace the running exe and restart."""
        current_exe = sys.executable

        # If running from source (python.exe), we can't really 'update' the exe.
        # This only works if frozen with PyInstaller.
        if not getattr(sys, "frozen", False):
            logging.warning("Not running as frozen application. Skipping update.")
            logging.info(
                "Mock update: would replace %s with %s", current_exe, new_exe_path
            )
            return

        batch_script_path = os.path.join(self._temp_dir, "update.bat")
        script_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
:retry
del "{current_exe}"
if exist "{current_exe}" (
    timeout /t 1 /nobreak > NUL
    goto retry
)
move "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
        with open(batch_script_path, "w") as f:
            f.write(script_content)

        logging.info("Executing update script and exiting...")
        subprocess.Popen([batch_script_path], shell=True)
        sys.exit(0)

    def cleanup(self):
        try:
            shutil.rmtree(self._temp_dir)
        except Exception:
            pass
