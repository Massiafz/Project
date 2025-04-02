@echo off
REM Build script for BrightByte Music Cataloging Software (Windows version)
REM This script checks for required dependencies (Pillow and PyInstaller),
REM installs them if necessary, builds an executable from main.py using PyInstaller,
REM packages necessary files, and then automatically launches the application.

REM Check if Pillow is installed by attempting an import.
python -c "import PIL" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    echo Pillow not found. Installing Pillow...
    pip install Pillow
)

REM Check if PyInstaller is installed.
pyinstaller --version >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing PyInstaller...
    pip install pyinstaller
)


REM Build the executable with PyInstaller.
REM Note: On Windows, the separator for --add-data is a semicolon (;).
pyinstaller --onefile --windowed ^
    --hidden-import PIL._tkinter_finder ^
    --add-data "users.json;." ^
    --add-data "cleaned_music_data.csv;." ^
    --add-data "BrightByteLogo.png;." ^
    --add-data "Eric.png;." ^
    main.py

echo Build complete! Launching the application...
start "" ".\dist\main.exe"
pause
