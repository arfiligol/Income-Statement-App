import os
import shutil
import subprocess
import zipfile
import re
from pathlib import Path


def get_version():
    """Read version from pyproject.toml"""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'version = "(.*?)"', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error reading version: {e}")
    return "0.0.0"


def clean():
    """Clean dist directory"""
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("Cleaning dist directory...")
        shutil.rmtree(dist_dir)


def build():
    """Run nicegui-pack"""
    print("Building application...")

    # Ensure dependencies are installed
    subprocess.run(["uv", "sync"], check=True)

    cmd = [
        "uv",
        "run",
        "nicegui-pack",
        "--name",
        "Income-Statement-App",
        "--icon",
        "src/static/mom_accounting.ico",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--add-data",
        f"src{os.sep}ui{os.sep}styles{os.pathsep}ui{os.sep}styles",
        "--add-data",
        f"src{os.sep}static{os.pathsep}static",
        os.path.join("src", "main.py"),
    ]

    print(f"Running command: {' '.join(cmd)}")

    # Add src to PYTHONPATH so PyInstaller can find modules like 'ui'
    env = os.environ.copy()
    src_path = os.path.abspath("src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = src_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = src_path

    subprocess.run(cmd, check=True, env=env)


import platform


def package_zip(version):
    """Zip the output"""
    app_name = "Income-Statement-App"

    # Determine platform string
    system = platform.system().lower()
    if system == "darwin":
        plat_name = "macos"
    elif system == "windows":
        plat_name = "windows"
    else:
        plat_name = system

    src_dir = Path("dist") / app_name
    # Income-Statement-App_windows_0.2.1.zip
    zip_name = f"{app_name}_{plat_name}_{version}.zip"
    zip_path = Path("dist") / zip_name

    if not src_dir.exists():
        print(f"Error: Build output not found at {src_dir}")
        return

    print(f"Compressing to {zip_path}...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(Path("dist"))
                zf.write(file_path, arcname)

    print(f"Success! Package created at: {zip_path}")


def main():
    try:
        clean()
        version = get_version()
        print(f"Detected version: {version}")

        build()
        package_zip(version)

    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()
