#!/usr/bin/env bash
#
# Development environment setup for macOS and Linux.
#
#   ./setup.sh              install what is missing, set up both environments, run the tests
#   ./setup.sh --check      report what is installed and what is out of date, change nothing
#   ./setup.sh --tauri      also set up the Rust toolchain for desktop development
#   ./setup.sh --help       full option list
#
# This script only bootstraps bun and uv, because the rest of the setup is
# written in TypeScript and needs bun to run. Everything after that lives in
# scripts/setup.ts, so there is one copy of the real logic rather than one per
# platform. Nothing here uses sudo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CHECK_ONLY=0
ASSUME_YES=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
    --yes|-y) ASSUME_YES=1 ;;
    --help|-h)
      exec bun "$SCRIPT_DIR/scripts/setup.ts" --help 2>/dev/null ||
        { echo "Install bun first: https://bun.com/docs/installation"; exit 1; }
      ;;
  esac
done

missing=0

if ! command -v git >/dev/null 2>&1; then
  echo "error: git is not installed. Install it with your package manager, then re-run." >&2
  exit 1
fi

# Make sure a tool is available, offering to install it if it is not. $3 is the
# directory its installer drops binaries into, so a tool installed in this same
# session can be used without opening a new shell.
ensure_tool() {
  local name="$1" installer="$2" bindir="$3"

  if command -v "$name" >/dev/null 2>&1; then
    return 0
  fi

  # Installed previously, but this shell's PATH predates it.
  if [ -x "$bindir/$name" ]; then
    export PATH="$bindir:$PATH"
    echo "note: using $bindir/$name (not on your PATH — add it to your shell profile)"
    return 0
  fi

  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "  missing: $name"
    missing=1
    return 0
  fi

  if [ "$ASSUME_YES" -ne 1 ]; then
    if [ ! -t 0 ]; then
      echo "error: $name is not installed, and there is no terminal to ask on." >&2
      echo "       Re-run with --yes to install it, or install it yourself:" >&2
      echo "         $installer" >&2
      exit 1
    fi
    echo ""
    echo "$name is not installed. It can be installed with:"
    echo "  $installer"
    printf "Install it now? [y/N] "
    read -r reply
    case "$reply" in
      [yY]|[yY][eE][sS]) ;;
      *)
        echo "Aborted. Install $name yourself, then re-run this script."
        exit 1
        ;;
    esac
  fi

  echo ">>> Installing $name"
  sh -c "$installer"
  export PATH="$bindir:$PATH"

  if ! command -v "$name" >/dev/null 2>&1; then
    echo "error: $name still is not on PATH after installing." >&2
    echo "       Open a new terminal and re-run this script." >&2
    exit 1
  fi
}

ensure_tool bun "curl -fsSL https://bun.com/install | bash" "$HOME/.bun/bin"
ensure_tool uv "curl -LsSf https://astral.sh/uv/install.sh | sh" "$HOME/.local/bin"

if [ "$CHECK_ONLY" -eq 1 ] && [ "$missing" -eq 1 ]; then
  echo ""
  echo "Install the missing tools by running ./setup.sh without --check."
  exit 1
fi

exec bun "$SCRIPT_DIR/scripts/setup.ts" "$@"
