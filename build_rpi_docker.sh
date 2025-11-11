#!/bin/bash

# Cross-compile spotigui for Raspberry Pi 4 using Docker + QEMU on macOS
# This script builds an ARM64 executable without needing a Raspberry Pi

set -e  # Exit on error

echo "============================================================"
echo "Cross-compiling spotigui for Raspberry Pi 4 (ARM64)"
echo "Using Docker + QEMU emulation"
echo "============================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "  https://www.docker.com/products/docker-desktop/"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker is not running"
    echo ""
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✓ Docker is installed and running"
echo ""

# Check if Docker buildx is available (for multi-platform builds)
if ! docker buildx version &> /dev/null; then
    echo "Setting up Docker buildx for multi-platform builds..."
    docker buildx create --name arm-builder --use 2>/dev/null || true
    docker buildx inspect --bootstrap
fi

echo "✓ Docker buildx is ready"
echo ""

# Check if QEMU is set up for ARM emulation
echo "Checking QEMU setup for ARM emulation..."
# Use the install command which is more reliable
if docker run --rm --privileged multiarch/qemu-user-static --reset -p yes 2>/dev/null; then
    echo "✓ QEMU ARM emulation is ready"
else
    echo "Setting up QEMU using alternative method..."
    # Try using docker buildx which has built-in QEMU support
    docker buildx inspect --bootstrap 2>/dev/null || docker buildx create --name multiarch --driver docker-container --use
    echo "✓ Using Docker buildx for multi-platform support"
fi
echo ""

# Build image name
IMAGE_NAME="spotigui-rpi-builder"
CONTAINER_NAME="spotigui-rpi-build"

# Clean up any existing container
echo "Cleaning up previous builds..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Build the Docker image for ARM64
echo ""
echo "Building Docker image for ARM64..."
echo "This will take 20-40 minutes on first run (downloads ARM packages, compiles Kivy)"
echo "Subsequent builds will be faster thanks to Docker caching."
echo ""
echo "Starting build at: $(date)"
echo ""

# Try using buildx for better multi-platform support
if docker buildx version &> /dev/null; then
    echo "Using docker buildx for multi-platform build..."
    docker buildx build \
        --platform linux/arm64 \
        --load \
        -t $IMAGE_NAME \
        -f Dockerfile.rpi \
        .
else
    echo "Using standard docker build..."
    docker build \
        --platform linux/arm64 \
        -t $IMAGE_NAME \
        -f Dockerfile.rpi \
        .
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Docker build failed"
    exit 1
fi

echo ""
echo "✓ Docker image built successfully"
echo ""

# Run the container to build the executable
echo "Running build container..."
docker run \
    --platform linux/arm64 \
    --name $CONTAINER_NAME \
    $IMAGE_NAME

# Create output directory
mkdir -p dist-rpi

# Copy the built executable from the container
echo ""
echo "Extracting built executable..."
docker cp $CONTAINER_NAME:/build/dist/spotigui ./dist-rpi/

# Clean up container
docker rm $CONTAINER_NAME

# Make executable
chmod +x dist-rpi/spotigui

echo ""
echo "============================================================"
echo "Build complete!"
echo "============================================================"
echo ""
echo "Output: dist-rpi/spotigui"

# Get file info
if [ -f "dist-rpi/spotigui" ]; then
    SIZE=$(du -h dist-rpi/spotigui | cut -f1)
    echo "Size: $SIZE"

    # Verify it's ARM64
    FILE_INFO=$(file dist-rpi/spotigui)
    echo "Type: $FILE_INFO"

    echo ""
    echo "This executable is for Raspberry Pi 4 (ARM64/aarch64)"
    echo ""
    echo "To transfer to your Raspberry Pi:"
    echo "  scp dist-rpi/spotigui pi@raspberrypi.local:~/"
    echo ""
    echo "Then on your Raspberry Pi:"
    echo "  chmod +x ~/spotigui"
    echo "  ./spotigui"
    echo ""
    echo "Note: Don't forget to copy your .env file with Spotify credentials!"
else
    echo "ERROR: Build output not found"
    exit 1
fi

echo ""
echo "Build completed at: $(date)"
