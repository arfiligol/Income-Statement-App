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
        self._cancelled = False

    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check GitHub for the latest release."""
        try:
            logging.info("Checking for updates from %s...", GITHUB_API_URL)
            response = requests.get(GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version = data["tag_name"].lstrip("v")

            # Simple semantic version comparison
            def parse_version(v):
                return tuple(map(int, (v.split("."))))

            try:
                if parse_version(latest_version) <= parse_version(self.current_version):
                    logging.info(
                        "App is up to date (version %s).", self.current_version
                    )
                    return None
            except ValueError:
                # Fallback for non-standard versions
                if latest_version == self.current_version:
                    return None

            # Find the MSI asset
            msi_asset = next(
                (asset for asset in data["assets"] if asset["name"].endswith(".msi")),
                None,
            )

            if not msi_asset:
                logging.warning(
                    "New release found (%s) but no .msi asset.", latest_version
                )
                return None

            update_info = UpdateInfo(
                version=latest_version,
                download_url=msi_asset["browser_download_url"],
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

    def cancel_update(self):
        """Cancel the ongoing update process."""
        self._cancelled = True
        logging.info("Update cancellation requested.")

    def perform_update(
        self,
        update_info: UpdateInfo,
        progress_callback: Optional[callable] = None,
        error_callback: Optional[callable] = None,
        completion_callback: Optional[callable] = None,
    ) -> None:
        """Download and install the update in a background thread."""
        self._cancelled = False
        thread = Thread(
            target=self._download_and_install,
            args=(update_info, progress_callback, error_callback, completion_callback),
        )
        thread.start()

    def _download_and_install(
        self,
        update_info: UpdateInfo,
        progress_callback: Optional[callable] = None,
        error_callback: Optional[callable] = None,
        completion_callback: Optional[callable] = None,
    ) -> None:
        try:
            download_path = os.path.join(self._temp_dir, "MomWorkProject_Setup.msi")
            logging.info("Downloading update from %s...", update_info.download_url)

            with requests.get(update_info.download_url, stream=True) as r:
                r.raise_for_status()
                total_length = r.headers.get("content-length")

                with open(download_path, "wb") as f:
                    if total_length is None:  # no content length header
                        f.write(r.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for chunk in r.iter_content(chunk_size=8192):
                            if self._cancelled:
                                logging.info("Download cancelled by user.")
                                return

                            dl += len(chunk)
                            f.write(chunk)
                            if progress_callback:
                                # Let's do 0-100 for download
                                done = int(100 * dl / total_length)
                                progress_callback(done)

            if self._cancelled:
                return

            logging.info("Download completed.")
            if completion_callback:
                completion_callback(download_path)
            else:
                self.launch_installer_and_exit(download_path)

        except Exception as e:
            logging.error("Update failed: %s", e)
            if error_callback:
                error_callback(str(e))

    def launch_installer_and_exit(self, msi_path: str) -> None:
        """Launch the MSI installer and exit the application."""
        try:
            logging.info("Starting installer: %s", msi_path)
            os.startfile(msi_path)
            # Give the installer a moment to start before killing the app
            time.sleep(2)
            sys.exit(0)
        except Exception as e:
            logging.error("Failed to launch installer: %s", e)

    def cleanup(self):
        try:
            shutil.rmtree(self._temp_dir)
        except Exception:
            pass
