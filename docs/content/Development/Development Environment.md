# Development Setup

This guide sets up the current Device Bay software development environment on a fresh Windows, macOS, or Linux machine.

It covers:

- browser-based GUI development
- FastAPI backend development
- optional Tauri desktop development

The current software layout is:

```folder
docs
sites
└── docs
software/
├── client/
└── gui/
    ├── backend/
    └── frontend/
```
- `sites/docs` contains the parent quartz website repository as a submodule. This way, the submodule only needs to be downloaded if the website is being built locally. For most development this likely isn't needed, and the work of building the website is handled by github actions. By using a submodule, the latest version of quartz is always used so that explicit updating steps are not required. The `sites/` directory could also contain files related to other websites in the future.
- `docs` contains this documentation as an obsidian vault. During a commit to the main branch, the contents of `docs` is copied into corresponding folders in `sites/docs/` and built into a website with quartz.
- `software/client/` is the reusable Python `dbay` package.
- `software/gui/backend/` is the FastAPI backend and Python packaging project.
- `software/gui/frontend/` is the Svelte frontend and Tauri desktop app.

## 1. Install Core Tools

### Git

Install Git using your platform's normal installer or package manager, then verify:

```bash
git --version
```

### Bun

The frontend and GUI build scripts use Bun.
See the official Bun installation guide: [bun.com/docs/installation.md](https://bun.com/docs/installation.md)

#### macOS and Linux

```bash
curl -fsSL https://bun.com/install | bash
```

#### Windows PowerShell

```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

Restart your terminal if needed, then verify:

```bash
bun --version
```

### uv

The backend uses `uv` for Python version management, virtual environment creation, and dependency installation.

See the official uv installation guide: [docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

#### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal if needed, then verify:

```bash
uv --version
```

### Python

The backend currently requires Python `>=3.11,<3.14`.

If your machine does not already have a compatible Python installed, `uv` can install one for you:

```bash
uv python install 3.11
```

Python `3.11` is the safest default for development. Python `3.12` and `3.13` should also be valid for this project.

## 2. Clone the Repository

```bash
git clone https://github.com/bkorzh/dbay.git
cd dbay
```

## 3. Set Up the Backend Environment

From the repository root:

```bash
cd software/gui/backend
uv sync
```

This creates the local `.venv` and installs the backend dependencies from `pyproject.toml`.

It also installs the local `software/client/` package as an editable dependency, because the backend reuses that package internally.

If `uv sync` reports that no compatible Python is available, run:

```bash
uv python install 3.11
uv sync
```

## Why This Project Standardizes on `uv`

This project intentionally standardizes on `uv` instead of supporting multiple Python environment managers.

Reasons:

- the backend already declares its dependencies in `software/gui/backend/pyproject.toml`
- the backend development scripts already run through `uv`
- the CI and release workflow already use `uv sync`
- consistent environment creation helps keep local development and PyInstaller packaging reproducible

That last point matters here. The packaged GUI depends on PyInstaller collecting the right Python environment contents into the backend executable. If contributors build the environment in different ways, the resulting installed packages and interpreter layout can differ, which makes packaged builds less predictable.

If you are curious why `uv` is a strong default even outside this repository, this article is a good overview: [uv is the best thing to happen to the Python ecosystem in a decade](https://emily.space/posts/251023-uv).

## 4. Set Up the Frontend Environment

From the repository root:

```bash
cd software/gui/frontend
bun install
```

This installs the Svelte, Vite, and Tauri JavaScript dependencies.

## 5. Build the Static Frontend When Needed

Browser development does not require a prebuilt frontend, because Vite serves the UI directly.

However, the FastAPI backend cannot serve the built UI directly until the frontend has been compiled at least once into:

- `software/gui/backend/backend/compiled_frontend/`

If you want to:

- run the backend against compiled frontend files
- package the backend
- prepare a Tauri build

run the frontend build first.

### macOS and Linux

From the repository root:

```bash
./software/gui/build.sh frontend
```

### Windows PowerShell

From the repository root:

```powershell
cd software/gui/frontend
bun run buildfrontend
```

The same wrapper script also supports:

```bash
./software/gui/build.sh backend
./software/gui/build.sh tauri
./software/gui/build.sh all
```

## 6. Start the App

### Browser Development

Browser development means:

- the frontend is served by the Vite development server
- the backend runs separately as an API server
- you open the app in a normal web browser at `http://localhost:5173`

This is usually the fastest way to work on the GUI and backend together.

This mode starts:

- the FastAPI backend on port `8345`
- the Vite development server on port `5173`

### macOS and Linux

From the repository root:

```bash
./software/gui/dev-browser.sh
```

### Windows PowerShell

From the repository root:

```powershell
cd software/gui/frontend
bun run develop
```

Then open:

```text
http://localhost:5173
```

### Supported Backend Startup Paths

The supported ways to start the backend are the wrapper scripts and the FastAPI commands they call.

Use one of these approaches:

- `./software/gui/dev-browser.sh`
- `./software/gui/dev-tauri.sh`
- `uv run fastapi dev main.py ...`
- `uv run fastapi run main.py ...`

Do **not** treat `python software/gui/backend/backend/main.py` as the normal startup command.

That file is part of the `backend` Python package, and running it directly as a plain script can lead to confusing import-path issues that do not occur with the supported FastAPI entrypoints.

### Tauri Development

Use this mode only if you need to work on the desktop app shell or desktop packaging.

### macOS and Linux

From the repository root:

```bash
./software/gui/dev-tauri.sh
```

### Windows PowerShell

From the repository root:

```powershell
cd software/gui/frontend
bun run developtauri
```

This starts the same backend on port `8345` and opens the Tauri desktop window.

## 7. Tauri Desktop Prerequisites

If you only need browser-based frontend or backend development, you can skip this section.

Installing `@tauri-apps/cli` through `bun install` does **not** install the Rust toolchain or the native system packages required by Tauri.

The following mirrors the official Tauri prerequisites guide: [v2.tauri.app/start/prerequisites](https://v2.tauri.app/start/prerequisites)

### Rust

Install Rust separately.

#### macOS and Linux

```bash
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```

#### Windows

Install Rust with the official `rustup` installer from [rust-lang.org/tools/install](https://www.rust-lang.org/tools/install).

### Platform Notes

#### Windows

Tauri development also needs the Windows native prerequisites described in the Tauri docs, including Microsoft C++ build tools and WebView2.

#### macOS

Install the Xcode command line tools:

```bash
xcode-select --install
```

#### Linux

For Debian or Ubuntu, the repository CI currently installs:

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  libssl-dev \
  libgtk-3-dev \
  libwebkit2gtk-4.1-dev \
  libsoup-3.0-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libxdo-dev \
  patchelf
```

## 8. Verify the Setup

For browser development, a successful start usually means:

- the backend logs show FastAPI/Uvicorn listening on port `8345`
- the browser loads the app at `http://localhost:5173`

For Tauri development, a successful start usually means:

- the backend starts on port `8345`
- the desktop window opens successfully

The app can start without connected hardware. Hardware-dependent actions will not work until the source is initialized through the UI.

## 9. Troubleshooting

### `bun` or `uv` command not found

Restart the terminal first. If the command is still missing, check the official install docs above and confirm the install location is on your `PATH`.

### `uv sync` fails because Python is missing

Install a compatible Python with:

```bash
uv python install 3.11
```

Then rerun:

```bash
uv sync
```

### Tauri fails to start or build

This usually means Rust or native Tauri prerequisites are missing. Recheck the Tauri prerequisites guide for your operating system.

### Running `main.py` directly gives import errors

Use the supported startup commands above instead of running `python software/gui/backend/backend/main.py` directly.

If you need to start only the backend manually, use a FastAPI command such as:

```bash
cd software/gui/backend/backend
uv run fastapi dev main.py --port 8345 --host 0.0.0.0
```

or from the backend project root:

```bash
cd software/gui/backend
uv run python -m backend.main
```

The FastAPI command is the preferred manual workflow.

### Backend starts but complains that `compiled_frontend` assets are missing

That means you are trying to use the backend's static-serving path before the frontend has been built into:

- `software/gui/backend/backend/compiled_frontend/`

Fix that by running:

```bash
./software/gui/build.sh frontend
```

or on Windows:

```powershell
cd software/gui/frontend
bun run buildfrontend
```

### Port `5173` or `8345` is already in use

Stop the process already using that port, then rerun the development command.