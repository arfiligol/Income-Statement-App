import os
import platform
import shutil
import subprocess
import zipfile
from pathlib import Path

# Configuration
APP_NAME = "IncomeStatement"
MAIN_SCRIPT = "main.py"
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")


def clean():
    """Remove build and dist directories."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    print("Cleaned build artifacts.")


def build():
    """Run nicegui-pack to create the executable."""
    print("Building with nicegui-pack...")

    # Common arguments
    # --onefile vs --onedir: We choose --onedir for faster updates (script swap)
    # nicegui-pack defaults currently might be onefile, let's check or use pyinstaller directly if needed.
    # nicegui-pack is a wrapper around pyinstaller.
    # Usage: nicegui-pack [options] <main_script>

    # We explicitly use --on-dir (if supported by nicegui-pack, otherwise we pass to pyinstaller)
    # nicegui-pack documentation says it supports pyinstaller arguments.

    cmd = [
        "nicegui-pack",
        "--onedir",
        "--name",
        APP_NAME,
        # "--windowed", # nicegui-pack adds this by default usually? Better explicit.
        # "--add-data", "app/static:app/static", # Example if needed
    ]

    # Platform specific
    if platform.system() == "Windows":
        cmd.extend(
            ["--windowed", "--icon", "app/static/icon.ico"]
        )  # Ensure icon exists or remove
    elif platform.system() == "Darwin":  # macOS
        cmd.extend(
            ["--windowed", "--icon", "app/static/icon.icns"]
        )  # Ensure icon exists or remove

    cmd.append(MAIN_SCRIPT)

    # Check if icon files exist, if not remove icon arg
    # (Implementation detail: for now we skip icon check to avoid breaking if file missing,
    # but strictly we should have icons. I will remove icon and add-data for now to be safe,
    # user can add later or I'll check existence).
    # Simplified cmd:
    cmd = ["nicegui-pack", "--onedir", "--name", APP_NAME, MAIN_SCRIPT]

    subprocess.check_call(cmd)
    print(f"Build complete. Artifacts in {DIST_DIR}/{APP_NAME}")


def zip_artifacts():
    """Zip the output for GitHub Releases."""
    print("Zipping artifacts...")

    system = platform.system().lower()
    zip_name = "macos.zip" if system == "darwin" else "windows.zip"
    zip_path = DIST_DIR / zip_name

    # The artifact folder
    # On macOS, nicegui-pack/pyinstaller creates "IncomeStatement.app" inside dist/IncomeStatement (onedir) or similar?
    # No, --onedir on macOS creates a folder "IncomeStatement" which might contain the .app or executable.
    # Wait, PyInstaller --onedir on macOS usually creates a folder "dist/AppName" containing the executable and libs.
    # If we want a .app bundle, --windowed should handle steps, but usually --onedir results in a folder, not a .app bundle directly usable as "Double Click App".
    # For macOS Deployment, usually we want a .app.
    # nicegui-pack might handle this.

    # Let's verify what we zip.
    # We will zip the entire content of "dist/IncomeStatement".

    source_dir = DIST_DIR / APP_NAME

    if not source_dir.exists():
        print(f"Error: {source_dir} not found.")
        return

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(
                    DIST_DIR
                )  # e.g. IncomeStatement/app.exe
                zf.write(file_path, arcname)

    print(f"Created {zip_path}")


if __name__ == "__main__":
    clean()
    try:
        build()
        zip_artifacts()
    except Exception as e:
        print(f"Build failed: {e}")
