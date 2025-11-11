================================================================================
        Building spotigui for Raspberry Pi 4 (64-bit ARM)
================================================================================

QUICK START:

1. Transfer files to your Raspberry Pi:

   On your Mac, run:
   ./transfer_to_rpi.sh raspberrypi.local

   (Replace 'raspberrypi.local' with your Pi's IP address if needed)

2. SSH into your Raspberry Pi:

   ssh pi@raspberrypi.local
   cd ~/spotigui

3. Run the setup script (first time only):

   chmod +x setup_rpi.sh
   ./setup_rpi.sh

   This installs all dependencies (~20-30 minutes)

4. Create .env file with your Spotify credentials:

   nano .env

   Add:
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

5. Build the executable:

   ./build_rpi.sh

   Build takes ~5-10 minutes

6. Run the application:

   ./dist/spotigui

================================================================================
IMPORTANT NOTES:
================================================================================

- You CANNOT build Raspberry Pi executables from macOS (no cross-compilation)
- You MUST build directly on the Raspberry Pi
- Requires Raspberry Pi 4 with 64-bit OS (Raspbian Buster/Bullseye or newer)
- First launch extracts files and is slow; subsequent launches are faster
- The executable is ~200-300MB (includes all dependencies)

================================================================================
DOCUMENTATION:
================================================================================

- QUICK_START_RPI.md      - Quick reference guide
- BUILD_RASPBERRY_PI.md   - Comprehensive build instructions
- BUILDING.md             - Overview of all platform builds

================================================================================
TROUBLESHOOTING:
================================================================================

Cannot connect to Raspberry Pi:
  - Enable SSH: sudo raspi-config -> Interface Options -> SSH

Python version too old:
  - Need Python 3.8+, upgrade Raspbian to Buster or Bullseye

Kivy installation fails:
  - Install build tools: sudo apt-get install build-essential python3-dev

Display not found (SSH):
  - Run: export DISPLAY=:0 && ./dist/spotigui
  - Or use: ssh -X pi@raspberrypi.local

Application is slow:
  - Increase GPU memory: Edit /boot/config.txt, add gpu_mem=128
  - Use 64-bit OS
  - Close other applications

================================================================================
FILES INCLUDED:
================================================================================

Transfer & Setup:
  transfer_to_rpi.sh    - Transfer project from Mac to Raspberry Pi
  setup_rpi.sh          - Install dependencies on Raspberry Pi

Build:
  build_rpi.sh          - Build executable on Raspberry Pi
  spotigui_rpi.spec     - PyInstaller configuration for ARM64 Linux

Documentation:
  README_RASPBERRY_PI.txt  - This file (quick reference)
  QUICK_START_RPI.md       - Quick start guide
  BUILD_RASPBERRY_PI.md    - Detailed instructions
  BUILDING.md              - Multi-platform overview

================================================================================
NEED HELP?
================================================================================

See BUILD_RASPBERRY_PI.md for comprehensive troubleshooting and detailed
instructions.

Kivy on Raspberry Pi:
  https://kivy.org/doc/stable/installation/installation-rpi.html

PyInstaller issues:
  https://github.com/pyinstaller/pyinstaller/issues

================================================================================
