#!/usr/bin/env bash
set -euo pipefail

ALFRED_DIR="$HOME/.local/share/alfred"
VENV_DIR="$ALFRED_DIR/venv"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)/scripts"

echo "==> Installing alfred..."

# 1. Create install root
mkdir -p "$ALFRED_DIR"

# 2. Create virtualenv if missing
if [ ! -f "$VENV_DIR/bin/python" ]; then
  echo "==> Creating virtualenv..."
  python3 -m venv "$VENV_DIR"
fi

# 3. Install alfred package
echo "==> Installing alfred package..."
"$VENV_DIR/bin/pip" install --quiet -e "$(dirname "$0")"

# 4. Symlink the launcher
mkdir -p "$HOME/.local/bin"
ln -sf "$VENV_DIR/bin/alfred" "$HOME/.local/bin/alfred"
echo "==> Linked ~/.local/bin/alfred"

# 5. Hook into shell
HOOK_LINE="source \"$SCRIPTS_DIR/shell_hook.sh\""
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ]; then
    if ! grep -qF "$HOOK_LINE" "$rc" 2>/dev/null; then
      echo "" >>"$rc"
      echo "# alfred shell hook" >>"$rc"
      echo "$HOOK_LINE" >>"$rc"
      echo "==> Added hook to $rc"
    fi
  fi
done

# 6. Ensure ~/.local/bin is on PATH
case ":$PATH:" in
*:"$HOME/.local/bin":*) ;;
*) echo "==> Add ~/.local/bin to your PATH (e.g. in .bashrc): export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

echo "==> Done! Start a new shell or run: source ~/.bashrc"
