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
pyinstaller --onefile --distpath . --name brightbyte-windows --windowed ^
    --hidden-import PIL._tkinter_finder ^
    --add-data "./Code/users.json;." ^
    --add-data "./Code/cleaned_music_data.csv;." ^
    --add-data "./Code/BrightByteLogo.png;." ^
    --add-data "./Code/Eric.png;." ^
    ./Code/main.py

echo Build complete! Launching the application...
start "" ".\brightbyte-windows.exe"
