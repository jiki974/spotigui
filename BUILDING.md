# Building spotigui for Different Platforms

This document provides an overview of building spotigui executables for different platforms.

## Platform-Specific Build Guides

- **macOS (Intel/Apple Silicon)**: See `BUILD_README.md` and use `build.sh`
- **Raspberry Pi 4 (ARM64 Linux)**:
  - **Cross-compile from Mac**: See `QUICKSTART_DOCKER.md` and use `build_rpi_docker.sh` ⭐ RECOMMENDED
  - **Build on Pi**: See `BUILD_RASPBERRY_PI.md` or `QUICK_START_RPI.md`
- **Windows**: See `BUILD_README.md` (build on Windows machine)
- **Linux (x86_64)**: Similar to Raspberry Pi, use `spotigui_rpi.spec` as template

## Quick Reference

### macOS

```bash
# Build on Mac
./build.sh

# Output:
# - dist/spotigui.app (App Bundle - double-click to run)
# - dist/spotigui (Standalone executable)
```

### Raspberry Pi 4 - Method 1: Cross-Compile from Mac (RECOMMENDED ⭐)

```bash
# Build from your Mac using Docker
./build_rpi_docker.sh

# Transfer to Raspberry Pi
scp dist-rpi/spotigui pi@raspberrypi.local:~/
scp .env pi@raspberrypi.local:~/

# Run on Pi
ssh pi@raspberrypi.local
chmod +x ~/spotigui
./spotigui

# Output:
# - dist-rpi/spotigui (ARM64 executable)
```

**Requirements:** Docker Desktop installed on Mac
**Time:** 20-40 minutes (first build), 2-5 minutes (rebuilds)

### Raspberry Pi 4 - Method 2: Build on Pi

```bash
# On your Mac: Transfer files
./transfer_to_rpi.sh raspberrypi.local

# On Raspberry Pi: Setup and build
ssh pi@raspberrypi.local
cd ~/spotigui
./setup_rpi.sh
./build_rpi.sh

# Output:
# - dist/spotigui (Standalone executable)
```

**Requirements:** Physical Raspberry Pi access
**Time:** 30 minutes (setup), 40 minutes (first build), 10 minutes (rebuilds)

## Important Notes

### Cross-Compilation Support (NEW!)

**Traditional PyInstaller limitation:** Does not support cross-compilation natively.

**Our solution:** Docker + QEMU emulation allows cross-compilation:

- ✅ Can build Raspberry Pi executables from macOS (using Docker)
- ✅ Can build Linux ARM64 executables from macOS (using Docker)
- ❌ Cannot build macOS executables from Windows (no workaround)
- ❌ Cannot build Windows executables from Linux (no workaround)

You **must build on the target platform** or use an emulator/VM.

### Architecture Compatibility

Each build is specific to the architecture:

| Build Platform | Works On |
|----------------|----------|
| macOS (Apple Silicon) | macOS ARM64 only |
| macOS (Intel) | macOS x86_64 only |
| Raspberry Pi 4 (64-bit) | ARM64 Linux only |
| Linux x86_64 | x86_64 Linux only |
| Windows x86_64 | Windows x86_64 only |

### Resource Path Fix

All builds now use the `resource_path()` function from `src/spotigui/__init__.py` to correctly locate KV files and assets in both development and packaged environments.

If you add new KV files, use:
```python
from spotigui import resource_path
Builder.load_file(resource_path("src/spotigui/your_file.kv"))
```

## Build Files Reference

### Spec Files

- **spotigui.spec** - macOS/Windows/Linux x86_64 build configuration
- **spotigui_rpi.spec** - Raspberry Pi ARM64 build configuration

The main differences:
- macOS creates both executable and .app bundle
- Linux creates only executable
- Raspberry Pi includes SDL2-specific hidden imports

### Build Scripts

- **build.sh** - macOS build script
- **build_rpi.sh** - Raspberry Pi build script
- **setup_rpi.sh** - Raspberry Pi dependency installation script
- **transfer_to_rpi.sh** - Transfer project files to Raspberry Pi

### Documentation

- **BUILD_README.md** - Detailed macOS/Windows build instructions
- **BUILD_RASPBERRY_PI.md** - Comprehensive Raspberry Pi guide
- **QUICK_START_RPI.md** - Quick Raspberry Pi build reference
- **PACKAGING_SUMMARY.md** - Overview of packaging approach

## Build Output Sizes

Expected executable sizes:

- **macOS**: 100-200 MB (includes Python runtime, Kivy, KivyMD, etc.)
- **Raspberry Pi**: 200-300 MB (larger due to ARM architecture)
- **Windows**: 100-200 MB
- **Linux x86_64**: 150-250 MB

These sizes are normal for packaged Python GUI applications and ensure the app works without requiring users to install dependencies.

## Reducing Build Size

To reduce executable size:

1. Remove unused dependencies before building
2. Use `upx=True` in spec file (already enabled)
3. Strip debug symbols:
   ```bash
   strip dist/spotigui  # Linux/macOS
   ```
4. Exclude unnecessary data files in spec file

## Testing Builds

### Before Packaging

Always test the application in development mode first:

```bash
# Activate virtual environment
source myenv/bin/activate  # macOS/Linux
# or
myenv\Scripts\activate  # Windows

# Run the application
python src/spotigui/main.py
```

### After Packaging

Test the packaged executable:

```bash
# macOS
open dist/spotigui.app
# or
./dist/spotigui

# Linux/Raspberry Pi
./dist/spotigui

# Windows
dist\spotigui.exe
```

## Distribution

### macOS

Distribute the `.app` bundle:
1. Zip the app: `zip -r spotigui-macos.zip dist/spotigui.app`
2. Users extract and drag to Applications folder
3. Note: Unsigned apps show security warning (right-click -> Open)

### Raspberry Pi

Distribute as tarball:
1. `tar -czf spotigui-rpi4-arm64.tar.gz dist/spotigui`
2. Users extract and run
3. Include README with system requirements

### Code Signing (Optional)

For professional distribution:

**macOS:**
```bash
codesign --deep --force --sign "Developer ID Application: Your Name" dist/spotigui.app
```

**Windows:**
Requires code signing certificate from trusted CA.

## Environment Variables

All builds require a `.env` file with Spotify credentials:

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Users must create this file in:
- Same directory as executable
- Or user's home directory: `~/.spotigui/.env`

## Troubleshooting

### Build Fails

1. Check PyInstaller version: `pyinstaller --version`
2. Ensure all dependencies installed: `pip list`
3. Check for errors in build log
4. Try cleaning: `rm -rf build dist`

### Missing KV Files Error

If you see "FileNotFoundError: [Errno 2] No such file or directory: 'src/spotigui/...'":
- Ensure you're using `resource_path()` for all `Builder.load_file()` calls
- Rebuild with `./build.sh` or `./build_rpi.sh`

### App Won't Start

1. Run from terminal to see error messages
2. Check Console.app (macOS) or system logs
3. Verify `.env` file exists with valid credentials
4. Check file permissions: `chmod +x dist/spotigui`

## Getting Help

- **macOS Issues**: Check BUILD_README.md
- **Raspberry Pi Issues**: Check BUILD_RASPBERRY_PI.md or QUICK_START_RPI.md
- **PyInstaller Issues**: https://github.com/pyinstaller/pyinstaller/issues
- **Kivy Issues**: https://kivy.org/doc/stable/

## CI/CD Integration

For automated builds, see examples:
- GitHub Actions workflows (for Linux/Windows)
- Use self-hosted runners for macOS/ARM builds
- Docker for consistent build environments

## Summary

Building spotigui for different platforms requires:
1. Target platform hardware or VM
2. Python 3.8+ with dependencies installed
3. Running the appropriate build script
4. Testing the output executable
5. Distributing with documentation

Each platform has unique requirements - follow the platform-specific guides for best results.
