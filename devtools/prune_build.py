import os
import shutil
import glob


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def prune_pyside6():
    # Path to the PySide6 directory in the build folder
    # Adjust this path if your build path structure is different
    base_dir = os.path.join(
        os.getcwd(), "build", "src", "windows", "app", "src", "app_packages", "PySide6"
    )

    if not os.path.exists(base_dir):
        print(f"Error: PySide6 directory not found at {base_dir}")
        print("Make sure you have run 'briefcase update' first.")
        return

    print(f"Scanning PySide6 directory: {base_dir}")
    initial_size = get_size(base_dir)
    print(f"Initial size: {initial_size / 1024 / 1024:.2f} MB")

    # List of patterns to remove (glob patterns)
    # These are modules we likely don't need for a standard QtWidgets app
    patterns_to_remove = [
        # Large specific modules
        "QtWebEngine*",  # ~200MB+ (Browser engine)
        "Qt6WebEngine*",
        "Qt3D*",  # 3D Engine
        "Qt63D*",
        "QtQuick*",  # QML Engine (if strictly using QtWidgets)
        "Qt6Quick*",
        "QtQml*",  # QML Core
        "Qt6Qml*",
        # Tools and extras
        "designer.exe",  # Qt Designer
        "assistant.exe",  # Qt Assistant
        "linguist.exe",  # Translation tools
        "lupdate.exe",
        "lrelease.exe",
        "qml*",  # QML tools
        "uic.exe",
        # Other modules
        "*Multimedia*",  # Audio/Video
        "*Bluetooth*",
        "*Nfc*",
        "*Positioning*",
        "*Sensors*",
        "*SerialPort*",
        "*SerialBus*",
        "*Charts*",
        "*DataVisualization*",
        "*VirtualKeyboard*",
        "*TextToSpeech*",
        "*RemoteObjects*",
        "*WebChannel*",
        "*Scxml*",
        "*Help*",
        # "*Designer*",  # Kept for safety
        # "*UiTools*",   # Required by qt_material
        "*Test*",  # QtTest
        # Folders
        "examples",
        "glue",
        "include",  # Headers
        "scripts",
        "support",
        "translations",  # Maybe keep if you need Qt translations, but usually huge
        "typesystems",
    ]

    removed_count = 0

    for pattern in patterns_to_remove:
        # Search in the root of PySide6 dir (and bin/plugins/modules sometimes, but mostly they are flat or in specific subdirs)
        # glob.glob defaults to current dir if not absolute
        # We need to search recursively or just top level?
        # PySide6 layout on Windows:
        # - PySide6/ (pyds)
        # - PySide6/*.dll
        # - PySide6/plugins/...
        # - PySide6/translations/...

        # Let's target the base dir
        full_pattern = os.path.join(base_dir, pattern)
        matches = glob.glob(full_pattern)

        # Also verify if some DLLs are in subdirectories?
        # For Briefcase/pip installed PySide6 on Windows, most DLLs are in PySide6/ root.

        for match in matches:
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                else:
                    os.remove(match)
                removed_count += 1
                print(f"Removed: {os.path.basename(match)}")
            except Exception as e:
                print(f"Error removing {match}: {e}")

    final_size = get_size(base_dir)
    print("-" * 30)
    print(f"Pruning complete.")
    print(f"Final size: {final_size / 1024 / 1024:.2f} MB")
    print(f"Saved: {(initial_size - final_size) / 1024 / 1024:.2f} MB")
    print("-" * 30)


if __name__ == "__main__":
    prune_pyside6()
