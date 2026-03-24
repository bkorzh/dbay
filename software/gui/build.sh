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

cd "$SCRIPT_DIR/frontend"

case "$1" in
  frontend)
    exec bun run buildfrontend
    ;;
  backend)
    exec bun run buildbackend
    ;;
  tauri)
    exec bun run buildtauri
    ;;
  all)
    exec bun run buildall
    ;;
  *)
    usage
    exit 1
    ;;
esac
