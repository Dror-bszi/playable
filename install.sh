#!/bin/bash

set -e
USERNAME=$(whoami)

echo "🔧 Setting up PlayAble environment..."

# ─── System Dependencies ─────────────────────────
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    libatlas-base-dev \
    libjpeg-dev \
    bluetooth \
    bluez \
    bluez-tools \
    libhidapi-hidraw0 \
    libhidapi-libusb0 \
    expect \
    python3-uinput \
    pcmanfm \
    python3-picamera2 \
    libcamera-apps \
    python3-kms++ \
    python3-libcamera

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

# Make sure we’re using the latest stable toolchain
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
fi

# Cleanup
cd ~
rm -rf /tmp/evsieve-1.4.0*

# ─── Bluetooth Auto-Pair Setup ───────────────────
chmod +x "$(dirname "$0")/utils/pair_controller.expect"

# ─── Set PlayAble wallpaper ──────────────────────
echo "🖼 Setting PlayAble desktop background..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLPAPER_PATH="$SCRIPT_DIR/web/static/background.png"

mkdir -p /home/$USERNAME/Pictures
cp "$WALLPAPER_PATH" /home/$USERNAME/Pictures/playable-bg.png
chown $USERNAME:$USERNAME /home/$USERNAME/Pictures/playable-bg.png

# Try to set wallpaper if pcmanfm and a GUI session exist
if command -v pcmanfm &>/dev/null; then
    DISPLAY=:0 sudo -u $USERNAME pcmanfm --set-wallpaper /home/$USERNAME/Pictures/playable-bg.png || echo "⚠️ Failed to set wallpaper"
else
    echo "⚠️ pcmanfm not found, skipping wallpaper setup"
fi

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

# ─── Completion ───────────────────────────────────
echo ""
echo "✅ Installation complete!"
echo "👉 To run PlayAble:"
echo "   sudo -E python3 main.py"
