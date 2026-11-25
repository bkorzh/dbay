# Thin aliases for the real entry points in software/gui/. Everything here
# delegates, so build steps live in exactly one place (build.sh -> build.ts)
# and cannot drift out of sync with this file.

.PHONY: build serve build-python build-tauri build-all

# Build the frontend into backend/compiled_frontend/
build:
	cd ../.. && ./build.sh frontend

# Run the backend and the Vite dev server together (browser development)
serve:
	cd ../.. && ./dev-browser.sh

# Package the backend into a standalone executable with PyInstaller
build-python:
	cd ../.. && ./build.sh backend

# Build the Tauri desktop installers (expects a packaged backend)
build-tauri:
	cd ../.. && ./build.sh tauri

# Frontend, backend, and installers in sequence
build-all:
	cd ../.. && ./build.sh all
