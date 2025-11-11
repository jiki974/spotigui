# Quick Start: Building spotigui for Raspberry Pi 4

This is a condensed guide for building spotigui on your Raspberry Pi 4 (64-bit). For detailed information, see `BUILD_RASPBERRY_PI.md`.

## Important: No Cross-Compilation

⚠️ **You CANNOT build Raspberry Pi executables from macOS.** PyInstaller does not support cross-compilation. You must build directly on the Raspberry Pi.

## Method 1: Transfer and Build on Raspberry Pi (Recommended)

### Step 1: Transfer Files to Raspberry Pi

From your Mac, run:

```bash
./transfer_to_rpi.sh raspberrypi.local
# Or use IP address:
./transfer_to_rpi.sh 192.168.1.100
```

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
cd ~/spotigui
```

### Step 3: Run Setup Script

```bash
chmod +x setup_rpi.sh
./setup_rpi.sh
```

This will:
- Install system dependencies (SDL2, OpenGL, etc.)
- Create Python virtual environment
- Install Kivy, KivyMD, spotipy, and other Python packages
- Takes about 20-30 minutes on Raspberry Pi 4

### Step 4: Add Your Spotify Credentials

Create a `.env` file:

```bash
nano .env
```

Add your credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

### Step 5: Build the Executable

```bash
./build_rpi.sh
```

Build time: 5-10 minutes

### Step 6: Run the Application

```bash
./dist/spotigui
```

## Method 2: Manual Build on Raspberry Pi

If you prefer to set up manually:

```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libsdl2-dev \
    libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# 2. Create virtual environment
python3 -m venv myenv
source myenv/bin/activate

# 3. Install Python packages
pip install Cython==0.29.36
export USE_SDL2=1
pip install kivy[base] kivymd spotipy python-dotenv qrcode[pil] Pillow pyinstaller

# 4. Build
pyinstaller spotigui_rpi.spec

# 5. Run
./dist/spotigui
```

## Troubleshooting

### "Cannot connect to Raspberry Pi"

Enable SSH:
```bash
# On Raspberry Pi:
sudo raspi-config
# Navigate to: Interface Options -> SSH -> Enable
```

### "Python version too old"

Raspbian Jessie may have Python 3.5 or 3.7. You need at least Python 3.8+:
- Upgrade to Raspbian Buster or Bullseye (recommended)
- Or build Python 3.9+ from source

### "Kivy installation fails"

Install additional dependencies:
```bash
sudo apt-get install -y build-essential git python3-dev \
    libgl1-mesa-dev libgles2-mesa-dev
```

### "Display not found"

If running over SSH without display:
```bash
export DISPLAY=:0
./dist/spotigui
```

Or enable X11 forwarding:
```bash
ssh -X pi@raspberrypi.local
```

### "Application is slow"

Optimize Raspberry Pi:
1. Increase GPU memory: Edit `/boot/config.txt` and add `gpu_mem=128`
2. Use 64-bit OS for better performance
3. Close other applications
4. Use an SSD instead of SD card if possible

## Files Created

After successful build:
- **dist/spotigui** - Standalone executable (~200-300MB)
- Copy this to `/usr/local/bin/` for system-wide access

## Distribution

To share with other Raspberry Pi 4 users:

```bash
# Create tarball
tar -czf spotigui-rpi4-arm64.tar.gz dist/spotigui

# Transfer to another Pi
scp spotigui-rpi4-arm64.tar.gz pi@other-pi:~

# On the other Pi:
tar -xzf spotigui-rpi4-arm64.tar.gz
./dist/spotigui
```

## Desktop Integration

To add a desktop launcher:

```bash
mkdir -p ~/.local/share/applications
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
```

## Performance Tips

- **First launch is slow**: PyInstaller extracts files to temp directory
- **Subsequent launches are faster**: Files are cached
- **Fullscreen mode**: Better performance than windowed
- **Disable desktop effects**: Improves rendering performance

## Getting Help

- Full documentation: `BUILD_RASPBERRY_PI.md`
- Kivy on Raspberry Pi: https://kivy.org/doc/stable/installation/installation-rpi.html
- PyInstaller issues: https://github.com/pyinstaller/pyinstaller/issues

## Architecture Notes

Your build will be specific to:
- **OS**: Linux (Raspbian/Debian)
- **Architecture**: ARM64 (aarch64)
- **Display**: X11/Wayland required

The executable will NOT work on:
- Raspberry Pi 3 or older (32-bit ARM)
- x86/x64 systems (Intel/AMD)
- macOS or Windows

Each platform requires its own build.
