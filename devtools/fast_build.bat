@echo off
echo Starting Nuitka build for Mom Work Project...
echo This may take a few minutes for the first compilation.

uv run nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyside6 ^
    --include-package=pandas ^
    --nofollow-import-to=pandas.tests ^
    --windows-console-mode=force ^
    --output-dir=dist ^
    --output-filename=mom-work-project.exe ^
    --no-deployment-flag=self-execution ^
    src/app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Executable is located at: dist\mom-work-project.exe
) else (
    echo.
    echo Build failed!
)
pause
