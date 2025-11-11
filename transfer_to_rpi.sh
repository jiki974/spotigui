#!/bin/bash

# Script to transfer spotigui project to Raspberry Pi
# Usage: ./transfer_to_rpi.sh [pi_hostname_or_ip]

# Default hostname if not provided
RPI_HOST="${1:-raspberrypi.local}"
RPI_USER="pi"
RPI_PATH="~/spotigui"

echo "======================================"
echo "Transferring spotigui to Raspberry Pi"
echo "======================================"
echo ""
echo "Target: $RPI_USER@$RPI_HOST:$RPI_PATH"
echo ""

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    echo "ERROR: rsync is not installed"
    echo "Please install it with: brew install rsync"
    exit 1
fi

# Test connection
echo "Testing connection to Raspberry Pi..."
if ! ssh -o ConnectTimeout=5 "$RPI_USER@$RPI_HOST" "echo 'Connection successful'" 2>/dev/null; then
    echo "ERROR: Cannot connect to $RPI_USER@$RPI_HOST"
    echo ""
    echo "Please check:"
    echo "1. Your Raspberry Pi is powered on and connected to the network"
    echo "2. SSH is enabled on the Raspberry Pi (sudo raspi-config -> Interface Options -> SSH)"
    echo "3. The hostname or IP address is correct"
    echo ""
    echo "Usage: $0 [hostname_or_ip]"
    echo "Example: $0 192.168.1.100"
    echo "Example: $0 raspberrypi.local"
    exit 1
fi

echo "Connection successful!"
echo ""

# Create directory on Raspberry Pi
echo "Creating directory on Raspberry Pi..."
ssh "$RPI_USER@$RPI_HOST" "mkdir -p $RPI_PATH"

# Transfer files
echo "Transferring files (this may take a few minutes)..."
rsync -avz --progress \
    --exclude 'myenv/' \
    --exclude 'build/' \
    --exclude 'dist/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.git/' \
    --exclude '.DS_Store' \
    --exclude '*.app' \
    ./ "$RPI_USER@$RPI_HOST:$RPI_PATH/"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "Transfer complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. SSH into your Raspberry Pi:"
    echo "   ssh $RPI_USER@$RPI_HOST"
    echo ""
    echo "2. Navigate to the project directory:"
    echo "   cd $RPI_PATH"
    echo ""
    echo "3. Run the setup script:"
    echo "   chmod +x setup_rpi.sh"
    echo "   ./setup_rpi.sh"
    echo ""
    echo "4. After setup, build the application:"
    echo "   ./build_rpi.sh"
    echo ""
    echo "For detailed instructions, see BUILD_RASPBERRY_PI.md"
else
    echo ""
    echo "ERROR: Transfer failed"
    exit 1
fi
