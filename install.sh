#!/bin/bash

set -e
USERNAME=$(whoami)

echo "🔧 Setting up PlayAble environment..."

# ─── System Dependencies ─────────────────────────
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    libatlas-base-dev \
    libjpeg-dev \
    bluetooth \
    bluez \
    bluez-tools \
    libhidapi-hidraw0 \
    libhidapi-libusb0 \
    libusb-1.0-0-dev \
    libudev-dev \
    expect \
    python3-uinput \
    pcmanfm \
    python3-picamera2 \
    libcamera-apps \
    python3-kms++ \
    python3-libcamera \
    hostapd \
    dnsmasq

# ─── Python Packages ─────────────────────────────
pip3 install --break-system-packages --upgrade pip
pip3 install --break-system-packages -r requirements.txt
pip3 install --break-system-packages mediapipe

# ─── Install Evsieve ──────────────────────────────
echo "🎛️ Installing evsieve..."

# Check if rustup is installed; if not, remove system cargo/rustc and install rustup
if ! command -v rustup &> /dev/null; then
    echo "🧹 Removing system Rust toolchain (cargo/rustc)..."
    sudo apt remove -y cargo rustc || true

    echo "⬇️ Installing official Rust toolchain via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "✔️ rustup already installed"
    source "$HOME/.cargo/env"
fi

# Make sure we're using the latest stable toolchain
rustup install stable
rustup default stable

# Install evsieve build dependencies
sudo apt install -y libevdev2 libevdev-dev

# Download and compile evsieve
cd /tmp
wget https://github.com/KarsMulder/evsieve/archive/v1.4.0.tar.gz -O evsieve-1.4.0.tar.gz
tar -xzf evsieve-1.4.0.tar.gz
cd evsieve-1.4.0

echo "🛠 Building evsieve with cargo..."
if cargo build --release; then
    sudo install -m 755 -t /usr/local/bin target/release/evsieve
    echo "✅ evsieve installed to /usr/local/bin"
else
    echo "❌ Failed to build evsieve. You may need to reboot or retry manually."
    exit 1
fi

# Cleanup
cd ~
rm -rf /tmp/evsieve-1.4.0*

# ─── AI Camera Setup ─────────────────────────────
echo "📸 Setting up AI camera..."

# Add user to video group
sudo usermod -a -G video $USERNAME

# ─── Bluetooth Auto-Pair Setup ───────────────────
chmod +x "$(dirname "$0")/utils/pair_controller.expect"

# ─── Install pi-apps (optional) ──────────────────
if [ "$USERNAME" == "pi" ] && [ ! -d "/home/pi/pi-apps" ]; then
    echo "📦 Installing pi-apps (Raspberry Pi App Store)..."
    sudo -u pi bash -c 'wget -qO- https://raw.githubusercontent.com/Botspot/pi-apps/master/install | bash'
fi

# ─── Sudo Permissions for PlayAble Tools ─────────
declare -a CMDS=("evtest" "bluetoothctl" "hcitool" "rfkill" "iw")

echo "🔐 Configuring sudoers (no password) for: ${CMDS[*]}"
for CMD in "${CMDS[@]}"; do
    CMD_PATH=$(which $CMD 2>/dev/null)
    if [ -n "$CMD_PATH" ]; then
        ENTRY="$USERNAME ALL=(ALL) NOPASSWD: $CMD_PATH"
        if ! sudo grep -Fxq "$ENTRY" /etc/sudoers; then
            echo "$ENTRY" | sudo tee -a /etc/sudoers > /dev/null
            echo "✅ Added: sudo $CMD without password"
        else
            echo "✔️ Already allowed: sudo $CMD"
        fi
    else
        echo "⚠️ Command not found: $CMD (skipped)"
    fi
done

# ─── Install Services ───────────────────────────
echo "📦 Installing system services..."

# Make wifi fallback script executable
chmod +x "$(dirname "$0")/utils/wifi_fallback.sh"

# Install and enable services independently
sudo cp playable.service /etc/systemd/system/
sudo cp wifi-fallback.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable services (they will start on next boot)
sudo systemctl enable playable.service
sudo systemctl enable wifi-fallback.service

# ─── Verify Installation ─────────────────────────
echo "🔍 Verifying installation..."

# Check Python packages
echo "Checking Python packages..."
python3 -c "import cv2, mediapipe, flask, hidapi, evdev, numpy" 2>/dev/null || {
    echo "❌ Some Python packages are missing. Please run: pip3 install -r requirements.txt"
    exit 1
}

# Check camera access
echo "Checking camera access..."
if ! python3 -c "from picamera2 import Picamera2; picam2 = Picamera2(); print('Camera available' if picam2.sensor_modes else 'No camera found')" | grep -q "Camera available"; then
    echo "❌ No camera detected. Please check your camera connection."
    exit 1
fi

# Check evsieve installation
if ! command -v evsieve &> /dev/null; then
    echo "❌ evsieve not found in PATH"
    exit 1
fi

# ─── Completion ───────────────────────────────────
echo ""
echo "✅ Installation complete!"
echo "👉 PlayAble will start automatically on boot"
echo "👉 WiFi fallback will be available when no internet connection is detected"
echo "   SSID: PlayAble_AP"
echo "   Password: playable123"
echo ""
echo "⚠️ Note: You may need to reboot for all changes to take effect."
echo "   sudo reboot"
