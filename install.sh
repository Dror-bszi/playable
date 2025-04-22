# install.sh
#!/bin/bash

set -e

echo "🔧 Setting up PlayAble environment..."

# Update and install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libatlas-base-dev libjpeg-dev

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install --upgrade pip
pip install flask opencv-python mediapipe

echo "✅ Installation complete!"
echo "To run PlayAble:"
echo "  source .venv/bin/activate && python main.py"