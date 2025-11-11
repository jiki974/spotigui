#!/bin/bash

# Build script for spotigui
# This script packages the application using PyInstaller

set -e  # Exit on error

echo "======================================"
echo "Building spotigui..."
echo "======================================"

# Activate virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller spotigui.spec

echo "======================================"
echo "Build complete!"
echo "======================================"

if [ -f "dist/spotigui.app" ]; then
    echo "macOS App bundle created at: dist/spotigui.app"
    echo ""
    echo "You can run it with: open dist/spotigui.app"
elif [ -f "dist/spotigui" ]; then
    echo "Executable created at: dist/spotigui"
    echo ""
    echo "You can run it with: ./dist/spotigui"
fi

echo ""
echo "Note: Make sure to copy your .env file with Spotify credentials"
echo "to the same directory as the executable or app bundle."
