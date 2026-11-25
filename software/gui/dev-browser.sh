#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR/frontend"

# Keep the gitignored node_modules in sync with package.json (no-op when
# unchanged), so a pull that adds a dependency doesn't break the dev server.
bun install

exec bun run develop
