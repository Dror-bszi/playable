#update.sh
echo "📦 Updating PlayAble from GitHub..."

cd "$(dirname "$0")"

# Discard local changes (files tracked by git)
git reset --hard

# Remove untracked files and folders (like __pycache__)
git clean -fd

# Pull the latest changes
git pull origin main

echo "✅ Update complete!"
