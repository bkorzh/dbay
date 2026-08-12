---
order: 2
---

# Repository Tour

Where everything lives. This is the one page that describes the repository layout; other pages link here instead of repeating it.

## Top level

```folder
dbay/
├── docs/
├── firmware/
├── hardware/
├── scripts/
├── software/
│   ├── client/
│   └── gui/
├── readme/
├── sites/
├── setup.sh
└── setup.ps1
```

- `docs/` — the source for this documentation, as an Obsidian vault under `docs/content/`
- `firmware/` — code that runs on the rack hardware
- `hardware/` — hardware design and assembly information
- `scripts/` — `setup.ts` does the environment setup described in [[Start Here]]; `release.ts` bumps versions, stamps changelogs, and creates tags; `extract_changelog.py` feeds GitHub Release bodies. See [[Building and Packaging]]
- `setup.sh` / `setup.ps1` — one-command development setup. They only bootstrap Bun and `uv` (nothing else can run before those exist) and then hand off to `scripts/setup.ts`, so the platform-specific part stays small and the real logic has a single copy
- `software/` — everything that runs on a PC
- `readme/` — images used by the top-level `README.md`
- `sites/docs/` — the Quartz website repository, included as a Git submodule

## Software

```folder
software/
├── client/                  # the reusable Python `dbay` package (published to PyPI)
│   ├── dbay/
│   ├── examples/
│   ├── tests/
│   └── pyproject.toml
└── gui/
    ├── backend/
    │   ├── backend/         # the Starlette app and hardware controllers
    │   ├── tests/
    │   ├── pyproject.toml
    │   └── uv.lock
    ├── frontend/
    │   ├── src/             # the Svelte UI
    │   ├── src-tauri/       # the Tauri desktop shell
    │   ├── build.ts         # build orchestration
    │   ├── develop.ts       # development launcher
    │   └── package.json
    ├── build.sh
    ├── dev-browser.sh
    └── dev-tauri.sh
```

### `software/client/`

The reusable Python `dbay` package, usable on its own and used internally by the GUI backend. It supports two modes:

- **GUI mode** — connects to a running GUI backend over the lab-link WebSocket and works against the backend's authoritative state
- **direct mode** — sends ASCII commands straight to the mainframe over UDP or serial, with no shared state

The module state models (`Dac4DState`, `Dac16DState`, `Adc4DState`, and friends in `dbay/state.py`) live here and are imported by the backend, so there is one definition of the rack's data model rather than one per process.

### `software/gui/backend/`

The Starlette application: shared state, the lab-link sync endpoint, module controllers, command handlers, and the PyInstaller packaging configuration. `backend/backend/` is the importable Python package; `software/gui/backend/` is the `uv` project root, which is where you run `uv` commands from.

The compiled frontend is copied into `backend/backend/compiled_frontend/` so a packaged backend can serve the UI itself.

### `software/gui/frontend/`

The Svelte UI, the Bun scripts, and the Tauri desktop wrapper in `src-tauri/`. Module UI components live in `src/lib/modules_dbay/`, reusable addons (voltage source, voltage sense) in `src/lib/addons/`, and the sync plumbing in `src/sync/` and `src/state/`.

### Shell wrappers

`build.sh`, `dev-browser.sh`, and `dev-tauri.sh` in `software/gui/` are thin wrappers over the Bun scripts in `frontend/package.json`. They exist so you can work from the repository root without remembering which directory each command belongs in, and they run `bun install` first so a `git pull` that adds a dependency cannot leave you with a stale `node_modules`. They are Bash scripts, so on Windows either use Git Bash or call the underlying Bun scripts directly.

## Tooling

- **Bun** for the frontend, the dev launcher, and the build scripts
- **uv** for Python versions, environments, and dependencies
- **Rust** for Tauri desktop work only — see the optional section of [[Start Here]]

### Why `uv` specifically

The project standardizes on `uv` rather than supporting several Python environment managers:

- the backend already declares its dependencies in `software/gui/backend/pyproject.toml`
- the dev launcher and build scripts already shell out to `uv`
- CI uses `uv sync --locked`

That last point is the important one. The packaged desktop app depends on PyInstaller collecting the right environment contents into the backend executable. If contributors build environments in different ways, the installed packages and interpreter layout differ, and packaged builds stop being reproducible.

If you want the broader argument for `uv` outside this repository, [this overview](https://emily.space/posts/251023-uv) is a good read.

## Configuration and state on disk

- `software/gui/backend/backend/config/vsource_params.json` — the rack's IP address, port, and the `dev_mode` flag, read at startup
- `~/Library/Application Support/dbay` (macOS), `%APPDATA%\dbay` (Windows), `$XDG_DATA_HOME/dbay` (Linux) — the SQLite database holding persisted rack state between runs

Neither is in the repository. See [[Start Here]] for the `DBAY_PERSIST` environment variables that disable or relocate persistence.

## The documentation itself

`docs/content/` is an Obsidian vault. Open that folder as a vault to edit, and keep images in `docs/content/attachments/` — see [[Writing documentation]] for the Obsidian settings and the style guide.

Publishing is automatic: on every push to `main`, the `Deploy Quartz site to GitHub Pages` workflow copies `docs/*` into `sites/docs/` and builds the site with Quartz. `sites/docs` is a submodule so that the Quartz machinery only needs to be checked out when you want to build the site locally; day-to-day documentation work does not require it.
