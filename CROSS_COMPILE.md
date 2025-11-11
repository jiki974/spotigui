# Cross-Compiling spotigui for Raspberry Pi from macOS

This guide explains how to build ARM64 (Raspberry Pi 4) executables directly from your Mac using Docker + QEMU emulation.

## Overview

**Traditional PyInstaller limitation:** PyInstaller does not support cross-compilation natively.

**Our solution:** Use Docker with QEMU ARM64 emulation to build Raspberry Pi executables on your Mac. This creates a virtualized ARM64 Linux environment where the build happens.

## Prerequisites

### 1. Install Docker Desktop

Download and install Docker Desktop for Mac:
- **Website:** https://www.docker.com/products/docker-desktop/
- **Requirements:** macOS 11.0 or later (works on both Intel and Apple Silicon)

After installation:
1. Launch Docker Desktop
2. Wait for it to start (whale icon in menu bar)
3. Verify installation:
   ```bash
   docker --version
   docker info
   ```

### 2. System Requirements

- **macOS:** 11.0 (Big Sur) or later
- **RAM:** At least 8GB (16GB recommended)
- **Disk Space:** 10GB free space for Docker images and build cache
- **Time:** First build takes 20-40 minutes; subsequent builds are much faster

## Quick Start

### Step 1: Build for Raspberry Pi

From your project directory, simply run:

```bash
./build_rpi_docker.sh
```

This script will:
1. ✅ Check if Docker is installed and running
2. ✅ Set up QEMU for ARM64 emulation
3. ✅ Build a Docker image with all dependencies (Kivy, SDL2, etc.)
4. ✅ Compile your application inside the ARM64 container
5. ✅ Extract the executable to `dist-rpi/spotigui`

**First build:** 20-40 minutes (downloads packages, compiles Kivy for ARM)
**Subsequent builds:** 2-5 minutes (Docker caching speeds things up)

### Step 2: Transfer to Raspberry Pi

```bash
# Copy to Raspberry Pi
scp dist-rpi/spotigui pi@raspberrypi.local:~/

# Also copy your .env file
scp .env pi@raspberrypi.local:~/
```

### Step 3: Run on Raspberry Pi

```bash
# SSH to Raspberry Pi
ssh pi@raspberrypi.local

# Make executable
chmod +x ~/spotigui

# Run
./spotigui
```

## How It Works

### Docker + QEMU Architecture

```
┌─────────────────────────────────────────────────────┐
│  Your Mac (macOS, Intel or Apple Silicon)          │
│  ┌───────────────────────────────────────────────┐ │
│  │  Docker Desktop                               │ │
│  │  ┌─────────────────────────────────────────┐ │ │
│  │  │  QEMU ARM64 Emulator                    │ │ │
│  │  │  ┌───────────────────────────────────┐  │ │ │
│  │  │  │  ARM64 Debian Linux Container     │  │ │ │
│  │  │  │  - Install SDL2, OpenGL, etc.     │  │ │ │
│  │  │  │  - Install Python + Kivy          │  │ │ │
│  │  │  │  - Run PyInstaller                │  │ │ │
│  │  │  │  - Build ARM64 executable         │  │ │ │
│  │  │  └───────────────────────────────────┘  │ │ │
│  │  └─────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
              ↓ Extract
        dist-rpi/spotigui (ARM64 binary)
```

### What's Happening

1. **QEMU Translation:** QEMU translates ARM64 instructions to x86_64 (Intel Mac) or ARM64 (Apple Silicon) in real-time
2. **Docker Isolation:** The entire ARM64 Linux environment runs in a container
3. **Native Build:** From the container's perspective, it's building on a native ARM64 system
4. **Extraction:** The built executable is copied from the container to your Mac

## Performance Notes

### Build Times

| Stage | First Build | Subsequent Builds |
|-------|-------------|-------------------|
| Download ARM packages | 5-10 min | Cached (instant) |
| Compile Kivy | 10-20 min | Cached (instant) |
| Install dependencies | 3-5 min | Cached (instant) |
| Build with PyInstaller | 5-10 min | 2-5 min |
| **Total** | **20-40 min** | **2-5 min** |

### Why Is It Slower Than Native?

- **QEMU Emulation:** Translating ARM instructions has overhead (~5-10x slower than native)
- **Compilation:** Building Kivy from source for ARM takes time
- **Docker Layers:** Each step is cached, so rebuilds are much faster

### Optimization Tips

1. **Don't modify Dockerfile often:** Changes invalidate cache
2. **Use Docker caching:** Keep the image around for fast rebuilds
3. **Apple Silicon users:** Emulation is faster than Intel Macs
4. **Increase Docker resources:** Go to Docker Desktop → Settings → Resources

## Detailed Usage

### Building

```bash
# Standard build
./build_rpi_docker.sh

# View verbose output
./build_rpi_docker.sh 2>&1 | tee build.log

# Clean build (no cache)
docker system prune -a
./build_rpi_docker.sh
```

### Output

The executable is placed in `dist-rpi/spotigui`:

```bash
# Check the file
ls -lh dist-rpi/spotigui
file dist-rpi/spotigui

# Expected output:
# dist-rpi/spotigui: ELF 64-bit LSB executable, ARM aarch64, ...
```

### Transferring to Raspberry Pi

```bash
# Option 1: SCP
scp dist-rpi/spotigui pi@raspberrypi.local:~/
scp .env pi@raspberrypi.local:~/

# Option 2: Rsync (faster for multiple files)
rsync -avz dist-rpi/spotigui .env pi@raspberrypi.local:~/

# Option 3: USB drive
cp dist-rpi/spotigui /Volumes/USB_DRIVE/
# Then plug into Raspberry Pi
```

## Troubleshooting

### Docker Not Found

```
ERROR: Docker is not installed
```

**Solution:** Install Docker Desktop from https://www.docker.com/products/docker-desktop/

### Docker Not Running

```
ERROR: Docker is not running
```

**Solution:**
1. Launch Docker Desktop application
2. Wait for the whale icon to appear in menu bar
3. Try again

### Build Fails: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Check Docker status
docker info

# Restart Docker Desktop
# macOS: Click whale icon → Restart
```

### Build Fails: "exec user process caused: exec format error"

This means QEMU isn't set up properly.

**Solution:**
```bash
# Reset QEMU
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Try building again
./build_rpi_docker.sh
```

### Build Is Very Slow

**Solutions:**

1. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources
   - Increase CPUs to 4-6
   - Increase Memory to 8GB+

2. **Use Apple Silicon Mac:** ARM-to-ARM emulation is faster

3. **Check other processes:** Close memory-intensive applications

### Out of Disk Space

```
ERROR: No space left on device
```

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Remove old images
docker images
docker rmi <image_id>

# Check Docker disk usage
docker system df
```

### Build Succeeds But App Won't Run on Pi

1. **Check architecture:**
   ```bash
   # On Raspberry Pi
   uname -m  # Should be aarch64 or arm64
   ```

2. **Check OS version:**
   ```bash
   cat /etc/os-release
   # Should be Debian Buster, Bullseye, or newer
   ```

3. **Check dependencies:**
   ```bash
   # On Raspberry Pi
   ldd ~/spotigui | grep "not found"
   ```

4. **Check .env file:**
   ```bash
   # Make sure .env is in the same directory
   ls -la ~/.env ~/spotigui
   ```

### "Cannot open display"

**Solution:**
```bash
# On Raspberry Pi, set display
export DISPLAY=:0
./spotigui
```

## Advanced Usage

### Customizing the Build

Edit `Dockerfile.rpi` to:
- Change base image version
- Add additional system packages
- Modify Python version
- Change Kivy configuration

After changes:
```bash
./build_rpi_docker.sh
```

### Building for Different ARM Variants

To build for Raspberry Pi 3 (32-bit ARM):

1. Change Dockerfile base image:
   ```dockerfile
   FROM arm32v7/debian:bullseye
   ```

2. Update spec file for 32-bit

3. Rebuild

### Using Docker Compose

For more complex builds, create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  builder:
    build:
      context: .
      dockerfile: Dockerfile.rpi
      platforms:
        - linux/arm64
    volumes:
      - ./dist-rpi:/output
```

### CI/CD Integration

Use in GitHub Actions or other CI:

```yaml
# .github/workflows/build-rpi.yml
name: Build for Raspberry Pi
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      - name: Build
        run: ./build_rpi_docker.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: spotigui-rpi
          path: dist-rpi/spotigui
```

## Comparison: Docker vs Native Build

| Aspect | Docker (Mac) | Native (Raspberry Pi) |
|--------|--------------|----------------------|
| Setup time | 5 min | 30 min |
| First build | 30 min | 40 min |
| Rebuild | 3 min | 10 min |
| Convenience | ✅ Build from Mac | ❌ Need Pi access |
| Speed | ⚠️ Slower (emulation) | ✅ Native speed |
| Consistency | ✅ Reproducible | ⚠️ Varies by Pi setup |
| Requirements | Docker Desktop | Raspberry Pi hardware |

## When to Use Each Method

### Use Docker (This Method) When:
- ✅ You don't have immediate access to Raspberry Pi
- ✅ You want reproducible builds
- ✅ You're developing on Mac and want to test ARM builds
- ✅ You want to build for multiple architectures
- ✅ You're setting up CI/CD

### Use Native Build When:
- ✅ You need the fastest possible build times
- ✅ You're already working on the Raspberry Pi
- ✅ You don't want to install Docker
- ✅ You're troubleshooting Raspberry Pi-specific issues

## Docker Commands Reference

```bash
# List images
docker images

# Remove image
docker rmi spotigui-rpi-builder

# List containers
docker ps -a

# Remove container
docker rm spotigui-rpi-build

# View image size
docker images spotigui-rpi-builder

# Clean everything
docker system prune -a

# Check disk usage
docker system df

# View build cache
docker buildx du
```

## Summary

Cross-compilation from macOS is now possible using Docker + QEMU:

1. **Install Docker Desktop**
2. **Run:** `./build_rpi_docker.sh`
3. **Wait:** 20-40 minutes (first time), 2-5 minutes (subsequent)
4. **Output:** `dist-rpi/spotigui` (ARM64 executable)
5. **Transfer to Raspberry Pi and run**

This method gives you the convenience of building from your Mac without needing physical access to a Raspberry Pi during development. 🚀
