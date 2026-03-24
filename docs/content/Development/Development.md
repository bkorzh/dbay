# Development

This section covers software development for Device Bay.

## Start Here

- Use [[Development Setup]] to set up a fresh Windows, macOS, or Linux machine for frontend, backend, or Tauri desktop work.
- Use [[Software frontend and backend]] for a high-level map of the software stack and codebase.

## Current Repo Layout

```folder
dbay/
├── docs/
├── firmware/
├── hardware/
├── software/
│   ├── client/
│   └── gui/
│       ├── backend/
│       └── frontend/
└── sites/
```

- `docs/` contains the source for this documentation.
- `firmware/` contains code that runs on rack hardware.
- `hardware/` contains hardware design and assembly information.
- `software/client/` contains the reusable Python `dbay` client package.
- `software/gui/frontend/` contains the Svelte frontend, Bun scripts, and Tauri desktop app.
- `software/gui/backend/` contains the FastAPI backend and PyInstaller packaging configuration.

## Current Tooling

- Frontend and build scripts use Bun.
- Python environments use `uv`.
- Tauri desktop development also requires Rust and platform-specific native dependencies.

## Suggested Reading Order

1. [[Development Setup]]
2. [[Software frontend and backend]]
3. A custom-module authoring guide will be added separately.