#!/bin/bash

# Build script for spotigui on Raspberry Pi
# This script packages the application using PyInstaller for ARM64 Linux

set -e  # Exit on error

echo "======================================"
echo "Building spotigui for Raspberry Pi..."
echo "======================================"

# Check if running on ARM
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo "WARNING: This script is intended for ARM64 systems (Raspberry Pi 4)"
    echo "Current architecture: $ARCH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "myenv" ]; then
    echo "ERROR: Virtual environment 'myenv' not found"
    echo "Please create it first:"
    echo "  python3 -m venv myenv"
    echo "  source myenv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Set environment variables for Kivy on Raspberry Pi
export USE_SDL2=1
export USE_GSTREAMER=1
export KIVY_GL_BACKEND=sdl2

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller spotigui_rpi.spec

echo "======================================"
echo "Build complete!"
echo "======================================"

if [ -f "dist/spotigui" ]; then
    echo "Executable created at: dist/spotigui"

    # Make it executable
    chmod +x dist/spotigui

    # Get file size
    SIZE=$(du -h dist/spotigui | cut -f1)
    echo "File size: $SIZE"
    echo ""
    echo "You can run it with: ./dist/spotigui"
    echo ""
    echo "To install system-wide:"
    echo "  sudo cp dist/spotigui /usr/local/bin/"
else
    echo "ERROR: Executable not found at dist/spotigui"
    exit 1
fi

echo ""
echo "Note: Make sure to copy your .env file with Spotify credentials"
echo "to the same directory as the executable:"
echo "  cp .env dist/"
