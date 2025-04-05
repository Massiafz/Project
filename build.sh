#!/bin/bash
# Build script for BrightByte Music Cataloging Software
# This script checks for required dependencies (Pillow and PyInstaller),
# installs them if needed, finds the Python shared library (libpython3.12.so.1.0) on Linux,
# builds an executable from main.py using PyInstaller (including data, binary files, and hidden imports),
# and then automatically launches the application.
#
# Usage:
#   chmod +x build.sh
#   ./build.sh

# Check if Pillow (PIL) is installed; if not, install it.
if ! python3 -c "import PIL" &> /dev/null; then
    echo "Pillow not found. Installing Pillow..."
    pip install Pillow --break-system-packages
fi

# Check if PyInstaller is installed; if not, install it.
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing PyInstaller..."
    pip install pyinstaller --break-system-packages
fi



# Determine the correct separator for --add-data and --add-binary.
# Use ':' for Linux/macOS and ';' for Windows.
OS_TYPE=$(uname)
if [ "$OS_TYPE" == "Linux" ] || [ "$OS_TYPE" == "Darwin" ]; then
    SEP=":"
else
    SEP=";"
fi

# For Linux, try to find libpython3.12.so.1.0 using ldconfig.
ADD_BINARY_FLAG=""
if [ "$OS_TYPE" == "Linux" ]; then
    LIB_PYTHON=$(ldconfig -p | grep libpython3.12.so.1.0 | awk '{print $4}' | head -n 1)
    if [ -n "$LIB_PYTHON" ]; then
        echo "Found libpython3.12.so.1.0 at $LIB_PYTHON"
        ADD_BINARY_FLAG="--add-binary ${LIB_PYTHON}${SEP}."
    else
        echo "Warning: libpython3.12.so.1.0 not found. The executable may fail to run."
    fi
fi

# Run PyInstaller with the required options.
# The --hidden-import flag is added to include PIL._tkinter_finder, which is needed for ImageTk.
pyinstaller --onefile --distpath . --name brightbyte-linux --windowed \
    --hidden-import PIL._tkinter_finder \
    --add-data "./Code/users.json${SEP}." \
    --add-data "./Code/cleaned_music_data.csv${SEP}." \
    --add-data "./Code/BrightByteLogo.png${SEP}." \
    --add-data "./Code/Eric.png${SEP}." \
    $ADD_BINARY_FLAG \
    ./Code/main.py

echo "Build complete! Launching the application..."
./brightbyte-linux
