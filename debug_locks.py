import psutil
import sys
import os
from pathlib import Path


def check_locks(target_path):
    target = Path(target_path).resolve()
    print(f"Scanning for processes locking: {target}...")

    found = False
    for proc in psutil.process_iter(["pid", "name", "exe", "cwd"]):
        try:
            # Check CWD (Current Working Directory)
            try:
                if (
                    proc.cwd()
                    and target in Path(proc.cwd()).resolve().parents
                    or target == Path(proc.cwd()).resolve()
                ):
                    print(f"❌ LOCKED BY CWD: {proc.info['name']} (PID: {proc.pid})")
                    print(f"   Process CWD: {proc.cwd()}")
                    found = True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            # Check Open Files
            try:
                open_files = proc.open_files()
                for file in open_files:
                    if str(target) in file.path:
                        print(
                            f"❌ LOCKED BY FILE: {proc.info['name']} (PID: {proc.pid})"
                        )
                        print(f"   File: {file.path}")
                        found = True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found:
        print("✅ No locks found (that we have permission to see).")
        print("Note: Some system/antivirus locks might be invisible to this script.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Default to the dist folder location or let user input
        path = input("Enter path to check (e.g., dist/IncomeStatement): ").strip()
        if not path:
            # Try to guess common lock target based on recent logs?
            # Let's just default to current dir if empty
            path = "."

    check_locks(path)
