#!/usr/bin/env bash
set -euo pipefail

echo "==> Uninstalling alfred..."

ALFRED_DIR="$HOME/.local/share/alfred"
CONFIG_DIR="$HOME/.config/alfred"
HOOK_MARKER="# alfred shell hook"

# 1. Remove shell hooks
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ]; then
    sed -i "/$HOOK_MARKER/d" "$rc" 2>/dev/null || true
    sed -i '\|shell_hook.sh|d' "$rc" 2>/dev/null || true
    echo "==> Cleaned hooks from $rc"
  fi
done

# 2. Remove launcher symlink
rm -f "$HOME/.local/bin/alfred"
echo "==> Removed ~/.local/bin/alfred"

# 3. Remove package + venv
if [ -d "$ALFRED_DIR" ]; then
  rm -rf "$ALFRED_DIR"
  echo "==> Removed $ALFRED_DIR"
fi

# 4. Remove config (keep by default; remove with --purge)
if [ "${1:-}" = "--purge" ]; then
  rm -rf "$CONFIG_DIR"
  echo "==> Removed $CONFIG_DIR"
else
  echo "==> Kept $CONFIG_DIR (use --purge to remove)"
fi

echo "==> Done. alfred has been removed."
