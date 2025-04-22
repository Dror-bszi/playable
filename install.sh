# install.sh
#!/bin/bash

set -e

echo "🔧 Setting up PlayAble environment..."

# Update and install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip libatlas-base-dev libjpeg-dev

# Install Python requirements globally from requirements.txt
pip3 install --upgrade pip
pip3 install --break-system-packages -r requirements.txt


echo "✅ Installation complete!"
echo "To run PlayAble:"
echo "  python3 main.py"