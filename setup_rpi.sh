#!/bin/bash

# Setup script for building spotigui on Raspberry Pi 4
# Run this script first before building

set -e  # Exit on error

echo "======================================"
echo "Setting up Raspberry Pi for spotigui"
echo "======================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Update system
echo ""
echo "Step 1: Updating system packages..."
echo "This may take several minutes..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    pkg-config \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    libmtdev-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    xclip \
    xsel \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev

# Check Python version
echo ""
echo "Step 3: Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "WARNING: Python 3.8+ is recommended. You have Python $PYTHON_VERSION"
    echo "The application may not work properly with older Python versions."
fi

# Create virtual environment
echo ""
echo "Step 4: Creating virtual environment..."
if [ -d "myenv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv myenv
    echo "Virtual environment created successfully"
fi

# Activate virtual environment
echo ""
echo "Step 5: Installing Python dependencies..."
source myenv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Cython (required for Kivy)
echo "Installing Cython..."
pip install Cython==0.29.36

# Install dependencies from requirements.txt
echo "Installing Python dependencies (this may take 10-20 minutes on Raspberry Pi)..."
export USE_SDL2=1
export USE_GSTREAMER=1
pip install -r requirements.txt

# Install PyInstaller
echo "Installing PyInstaller..."
pip install pyinstaller

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Make sure you have a .env file with your Spotify credentials:"
echo "   SPOTIFY_CLIENT_ID=your_client_id"
echo "   SPOTIFY_CLIENT_SECRET=your_client_secret"
echo "   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback"
echo ""
echo "2. Test the application:"
echo "   source myenv/bin/activate"
echo "   python src/spotigui/main.py"
echo ""
echo "3. Build the executable:"
echo "   ./build_rpi.sh"
echo ""
echo "For more information, see BUILD_RASPBERRY_PI.md"
