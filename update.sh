#!/bin/bash

set -e

echo "🔄 Updating PlayAble..."

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if we're on the correct branch
BRANCH="new-camera"  # change to "main" if this becomes the default
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "🌿 Switching to branch '$BRANCH'..."
    git fetch
    git checkout "$BRANCH"
fi

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin "$BRANCH"

# Reinstall dependencies (safe to re-run)
echo "🔧 Reinstalling dependencies..."
chmod +x install.sh
./install.sh

echo "✅ Update complete! You can now run: sudo -E python3 main.py"
