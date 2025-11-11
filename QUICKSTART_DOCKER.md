# Quick Start: Cross-Compile for Raspberry Pi from macOS

Build Raspberry Pi 4 (ARM64) executables directly from your Mac using Docker.

## Prerequisites

1. **Install Docker Desktop:**
   - Download: https://www.docker.com/products/docker-desktop/
   - Launch Docker Desktop and wait for it to start

2. **Verify Docker is running:**
   ```bash
   docker --version
   ```

## Build Steps (3 Commands!)

### 1. Build the ARM64 executable

```bash
./build_rpi_docker.sh
```

⏱️ **First build:** 20-40 minutes (downloads ARM packages, compiles Kivy)
⏱️ **Subsequent builds:** 2-5 minutes (Docker caching)

### 2. Transfer to Raspberry Pi

```bash
scp dist-rpi/spotigui pi@raspberrypi.local:~/
scp .env pi@raspberrypi.local:~/
```

### 3. Run on Raspberry Pi

```bash
ssh pi@raspberrypi.local
chmod +x ~/spotigui
./spotigui
```

## That's It! 🎉

You just cross-compiled a Raspberry Pi application from your Mac.

## What Happens During Build?

```
Your Mac → Docker → QEMU ARM Emulator → ARM64 Linux → Build → dist-rpi/spotigui
```

The script:
1. Sets up QEMU for ARM64 emulation
2. Creates an ARM64 Debian container
3. Installs all dependencies (SDL2, Kivy, etc.)
4. Builds your application with PyInstaller
5. Extracts the executable to `dist-rpi/`

## Output

- **File:** `dist-rpi/spotigui`
- **Size:** ~200-300MB (includes all dependencies)
- **Architecture:** ARM64/aarch64 (Raspberry Pi 4 only)

## Troubleshooting

### Docker not installed?
```bash
# Install from:
open https://www.docker.com/products/docker-desktop/
```

### Docker not running?
```bash
# Start Docker Desktop app, then retry
```

### Build fails?
```bash
# Check Docker has enough resources:
# Docker Desktop → Settings → Resources
# Recommended: 4+ CPUs, 8GB RAM
```

### Still stuck?
See full documentation: `CROSS_COMPILE.md`

## Quick Commands

```bash
# Build for Raspberry Pi
./build_rpi_docker.sh

# Check output
file dist-rpi/spotigui
ls -lh dist-rpi/spotigui

# Transfer to Pi
scp dist-rpi/spotigui pi@YOUR_PI_IP:~/

# Clean Docker cache (if needed)
docker system prune -a
```

## Comparison with Other Methods

| Method | Setup | First Build | Rebuild |
|--------|-------|-------------|---------|
| **Docker (this)** | 5 min | 30 min | 3 min |
| Native on Pi | 30 min | 40 min | 10 min |
| Transfer to Pi | N/A | 30 min | 10 min |

**Advantage:** Build from your Mac, no Pi needed during development!

## Next Steps

- **Full guide:** See `CROSS_COMPILE.md` for details
- **Native build:** See `BUILD_RASPBERRY_PI.md` for building on Pi
- **Transfer script:** Use `./transfer_to_rpi.sh` to send entire project

---

**Note:** This requires Docker Desktop and ~10GB disk space. First build is slow due to emulation, but subsequent builds are much faster thanks to caching.
