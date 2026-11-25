#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: ./software/gui/build.sh <target>

Targets:
  frontend   Build the frontend and copy it into the backend's compiled_frontend directory
  backend    Build the packaged backend with PyInstaller
  tauri      Build the Tauri app installers (expects a built backend)
  all        Build frontend, backend, and Tauri installers
EOF
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

case "$1" in
  frontend)
    script=buildfrontend
    ;;
  backend)
    script=buildbackend
    ;;
  tauri)
    script=buildtauri
    ;;
  all)
    script=buildall
    ;;
  *)
    usage
    exit 1
    ;;
esac

cd "$SCRIPT_DIR/frontend"

# node_modules is gitignored, so a `git pull` that adds or bumps a dependency
# leaves a stale install behind. Installing here keeps it in sync (it's a no-op
# when nothing changed) instead of failing later with an unresolved import.
bun install

exec bun run "$script"
