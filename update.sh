#update.sh
echo "📦 Updating PlayAble from GitHub..."

cd "$(dirname "$0")"

# Discard local changes (optional safety)
git reset --hard

# Pull the latest changes
git pull origin dror-elbow-try

echo "✅ Update complete!"