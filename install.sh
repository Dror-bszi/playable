# install.sh
#!/bin/bash

set -e

echo "🔧 Setting up PlayAble environment..."

# ─── System Dependencies ─────────────────────────
# Python and pip for script execution
# libatlas-base-dev and libjpeg-dev for OpenCV performance
# libgl1 for OpenCV image rendering
# bluez and bluetooth packages for Bluetooth scanning/connection
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    libatlas-base-dev \
    libjpeg-dev \
    libgl1 \
    bluetooth \
    bluez \
    bluez-tools \
    libhidapi-hidraw0 \
    libhidapi-libusb0


# ─── Python Packages ─────────────────────────────
# Install dependencies using --break-system-packages (needed on Pi OS Bookworm)
pip3 install --break-system-packages --upgrade pip
pip3 install --break-system-packages -r requirements.txt

# ─── Completion ───────────────────────────────────
echo "✅ Installation complete!"
echo "To run PlayAble:"
echo "  python3 main.py"