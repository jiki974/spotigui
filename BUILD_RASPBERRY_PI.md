# Building spotigui for Raspberry Pi 4 (ARM64)

This guide explains how to build spotigui on your Raspberry Pi 4 running Raspbian Jessie (64-bit).

## Important Note on Cross-Compilation

**PyInstaller does not support cross-compilation.** You cannot build a Raspberry Pi executable from macOS or Windows. You must build directly on the Raspberry Pi or use a similar ARM64 Linux system (like using QEMU or Docker with ARM64 emulation).

## Prerequisites

### System Requirements
- Raspberry Pi 4 (64-bit)
- Raspbian Jessie (64-bit) or newer
- At least 2GB free disk space
- Internet connection for downloading dependencies

### Install System Dependencies

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.13 build dependencies (if not available, use Python 3.9+)
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
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
    libgles2-mesa-dev

# Install additional libraries for Kivy
sudo apt-get install -y \
    xclip \
    xsel \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev
```

## Build Instructions

### 1. Transfer Project to Raspberry Pi

Copy your project to the Raspberry Pi. You can use `scp`, `rsync`, or clone from git:

```bash
# Option 1: Clone from git (if you have a git repository)
git clone https://github.com/yourusername/spotigui.git
cd spotigui

# Option 2: Transfer from your Mac using rsync
# Run this on your Mac:
rsync -avz --exclude 'myenv' --exclude 'build' --exclude 'dist' \
    /Users/jackyhoareau/Documents/hypermuse/spotigui/ \
    pi@raspberrypi.local:~/spotigui/
```

### 2. Set Up Python Environment

```bash
cd ~/spotigui

# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 3. Install Dependencies

```bash
# Install Cython first (required for Kivy)
pip install Cython==0.29.36

# Install Kivy with specific flags for Raspberry Pi
export USE_SDL2=1
export USE_GSTREAMER=1
pip install --no-cache-dir kivy[base] kivy_examples

# Install other dependencies
pip install kivymd spotipy python-dotenv qrcode[pil] Pillow

# Install PyInstaller
pip install pyinstaller
```

### 4. Test the Application

Before building, test that the app runs:

```bash
# Set environment to use SDL2 (no console output)
export KIVY_NO_ARGS=1
export KIVY_NO_CONSOLELOG=1

# Run the app
python src/spotigui/main.py
```

If you encounter display issues, you may need to run it in X11:
```bash
export DISPLAY=:0
python src/spotigui/main.py
```

### 5. Build the Executable

Use the provided build script:

```bash
chmod +x build_rpi.sh
./build_rpi.sh
```

Or manually:

```bash
# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller spotigui_rpi.spec
```

The executable will be created at `dist/spotigui`.

## Running the Built Application

### Copy to Raspberry Pi Applications

```bash
# Make executable
chmod +x dist/spotigui

# Test it
./dist/spotigui

# Optional: Install system-wide
sudo cp dist/spotigui /usr/local/bin/
```

### Create Desktop Entry (Optional)

Create a desktop launcher:

```bash
cat > ~/.local/share/applications/spotigui.desktop <<EOF
[Desktop Entry]
Name=SpotiGUI
Comment=Spotify Remote Control
Exec=/home/pi/spotigui/dist/spotigui
Icon=/home/pi/spotigui/src/spotigui/icon.png
Terminal=false
Type=Application
Categories=Audio;AudioVideo;Music;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

## Troubleshooting

### Kivy Installation Issues

If Kivy fails to install, try building from source:

```bash
pip install --no-binary kivy kivy[base]
```

### SDL2 Not Found

If you get SDL2 errors:

```bash
sudo apt-get install --reinstall libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

### Python Version Too Old

Raspbian Jessie may have an old Python version. Install a newer version:

```bash
# Check Python version
python3 --version

# If < 3.8, install from deadsnakes PPA or build from source
# For Raspberry Pi, it's recommended to use at least Python 3.9+
```

### Performance Issues

The Raspberry Pi 4 is powerful enough to run Kivy apps, but:

1. **Use the 64-bit OS** for better performance
2. **Increase GPU memory** in `/boot/config.txt`:
   ```
   gpu_mem=128
   ```
3. **Disable desktop compositing** for better rendering performance
4. **Use fullscreen mode** to improve performance

### OpenGL ES Issues

If you get OpenGL errors:

```bash
# Check if OpenGL ES is available
glxinfo | grep OpenGL

# Install Mesa OpenGL ES
sudo apt-get install mesa-utils libgles2-mesa-dev
```

## Performance Optimization

### Reduce Bundle Size

The PyInstaller bundle on ARM can be large (200-300MB). To reduce size:

1. Remove unused dependencies before building
2. Use `upx` compression (already enabled in spec)
3. Strip debug symbols:
   ```bash
   find dist/spotigui -type f -executable -exec strip {} \;
   ```

### Startup Time

First launch may be slow. To improve:
- Pre-compile Python bytecode: `python -m compileall dist/spotigui`
- Use an SSD instead of SD card
- Increase swap if RAM is limited

## Alternative: Docker Build (Advanced)

If you want to build on your Mac using Docker with ARM64 emulation:

```bash
# Install QEMU for ARM emulation
brew install qemu

# Enable Docker buildx for multi-platform builds
docker buildx create --name arm-builder --use
docker buildx inspect --bootstrap

# Build using ARM64 container
docker buildx build --platform linux/arm64 -t spotigui-rpi .
```

This method is complex and slower but allows building from your Mac.

## Distribution

To distribute to other Raspberry Pi users:

1. **Create a tarball:**
   ```bash
   tar -czf spotigui-rpi4-arm64.tar.gz -C dist spotigui
   ```

2. **Create installation script:**
   ```bash
   ./create_installer.sh
   ```

3. Users extract and run:
   ```bash
   tar -xzf spotigui-rpi4-arm64.tar.gz
   ./spotigui
   ```

## Known Limitations

- **No macOS .app bundle**: Linux builds create single executables, not .app bundles
- **Architecture-specific**: ARM64 build only works on ARM64 systems
- **Display server required**: Needs X11 or Wayland (won't run headless)
- **First launch slow**: PyInstaller extracts files on first run

## Support

For Raspberry Pi-specific issues:
- Check Kivy documentation: https://kivy.org/doc/stable/installation/installation-rpi.html
- Raspberry Pi forums: https://forums.raspberrypi.com/
- PyInstaller ARM issues: https://github.com/pyinstaller/pyinstaller/issues
