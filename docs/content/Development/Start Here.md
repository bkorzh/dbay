---
order: 1
---

# Start Here

This page takes a fresh Windows, macOS, or Linux machine to a running Device Bay development environment. It is the only page you need to read to get started; the rest of the Development section is reference material you can reach for later.

Browser development is the default path: the Svelte frontend runs on the Vite dev server, the Python backend runs separately, and you use the app in a normal web browser. Only work on the desktop shell or installers needs Tauri, which is an optional section at the end.

No Device Bay hardware is required to run the app.

## In a hurry?

Clone the repository, then from its root:

```bash
./setup.sh                  # macOS, Linux
```

```powershell
.\setup.ps1                 # Windows
```

It checks for Git, Bun, and `uv` and offers to install the ones you are missing, installs a compatible Python if needed, sets up both environments, and finishes by running the two test suites so you know the result works. It asks before installing anything, never uses `sudo`, and is safe to run again at any time. Add `--tauri` if you also need the desktop toolchain, or `--help` for the full option list.

If it succeeds, skip to [starting the app](#5-start-the-app).

Everything below is what that script does, one step at a time. Walk through it if you want to understand what ends up on your machine, or if the script stopped partway. There is also a read-only diagnostic that changes nothing:

```bash
./setup.sh --check
```

## 1. Install the tools

You need Git, Bun, and `uv`. Everything else is installed by those.

### Git

Install with your platform's usual installer or package manager, then check:

```bash
git --version
```

### Bun

The frontend, the development launcher, and the build scripts all run on Bun. See [bun.com/docs/installation](https://bun.com/docs/installation.md).

macOS and Linux:

```bash
curl -fsSL https://bun.com/install | bash
```

Windows PowerShell:

```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

### uv

The backend uses `uv` for Python versions, virtual environments, and dependencies. See [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal, then confirm both tools are visible:

```bash
bun --version
uv --version
```

### Python

The backend requires Python `>=3.11,<3.14`. If you do not already have one, let `uv` install it:

```bash
uv python install 3.11
```

Python 3.11 is the safest default. Nothing in the project requires a newer version.

## 2. Clone the repository

```bash
git clone https://github.com/bkorzh/dbay.git
cd dbay
```

## 3. Create the backend environment

```bash
cd software/gui/backend
uv sync
```

This creates `.venv` and installs the backend dependencies from `pyproject.toml`, including the local `software/client/` package as an editable dependency — the backend uses that package internally to talk to hardware.

If `uv sync` says no compatible Python is available, run `uv python install 3.11` and try again.

## 4. Install the frontend dependencies

```bash
cd software/gui/frontend
bun install
```

The development and build scripts also run `bun install` themselves, so this step mainly gets your editor's TypeScript tooling working right away. It is a fast no-op once the packages are in place.

## 5. Start the app

macOS and Linux, from the repository root:

```bash
./software/gui/dev-browser.sh
```

Windows PowerShell:

```powershell
cd software/gui/frontend
bun run develop
```

Both run the same launcher, `software/gui/frontend/develop.ts`, which starts two processes:

- the backend on port `8345`
- the Vite dev server on port `5173`

Then open:

```text
http://localhost:5173
```

## 6. Confirm it actually works

A healthy start looks like this:

```text
INFO:     Will watch for changes in these directories: ['.../software/gui/backend/backend']
INFO:     Uvicorn running on http://0.0.0.0:8345 (Press CTRL+C to quit)

  VITE v7.3.5  ready in 634 ms
  ➜  Local:   http://localhost:5173/

INFO:     127.0.0.1:51944 - "WebSocket /sync/ws" [accepted]
```

The last line is the one that matters. `/sync/ws` is how the frontend attaches to the backend's shared state; if the browser is open but that line never appears, the UI will load and then sit empty. See [[Troubleshooting]].

You can also run both test suites, which need no hardware and no running server:

```bash
cd software/gui/backend && uv run pytest
cd software/gui/frontend && bun run test
```

## Working without hardware

The app starts, and the UI works, with no rack connected. Add modules, set voltages, and the UI behaves normally.

That works because of `dev_mode` in `software/gui/backend/backend/config/vsource_params.json`, which ships enabled. In `dev_mode` nothing goes on the wire: every hardware command is acknowledged locally with `+ok`, so commands succeed instantly and the state updates as though a rack replied. The same file holds the rack's address and port.

Turn `dev_mode` off (through the UI, or in that file) when you have real hardware. If you turn it off *without* a rack at the configured address, each hardware command waits on UDP timeouts before giving up, which shows up as a sluggish UI rather than a clear error.

## Your rack state is saved between runs

The backend persists its state to a small SQLite database in your user data directory (`~/Library/Application Support/dbay` on macOS, `%APPDATA%\dbay` on Windows, `$XDG_DATA_HOME/dbay` on Linux), so yesterday's module layout, names, and setpoints come back when you restart. This surprises people who expect a clean slate on every launch.

To disable persistence or move the database:

```bash
DBAY_PERSIST=0 ./software/gui/dev-browser.sh          # no persistence at all
DBAY_PERSIST_DB=/tmp/dbay_dev.db ./software/gui/dev-browser.sh
```

Output state is deliberately *not* restored: channel `activated` and `measuring` flags reset on startup, because the software cannot know whether the hardware is actually driving an output.

## Optional: Tauri desktop development

Skip this unless you are working on the desktop shell or building installers. Installing `@tauri-apps/cli` through `bun install` does **not** install Rust or the native system libraries Tauri needs.

This mirrors the official guide at [v2.tauri.app/start/prerequisites](https://v2.tauri.app/start/prerequisites).

### Rust

macOS and Linux:

```bash
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```

On Windows, use the `rustup` installer from [rust-lang.org/tools/install](https://www.rust-lang.org/tools/install). CI builds with Rust `1.89.0`, so that version is known to work.

### Platform prerequisites

- **macOS**: `xcode-select --install`
- **Windows**: Microsoft C++ build tools and WebView2, as described in the Tauri prerequisites
- **Linux** (Debian/Ubuntu), the same list CI installs:

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

### Run it

```bash
./software/gui/dev-tauri.sh
```

Windows PowerShell:

```powershell
cd software/gui/frontend
bun run developtauri
```

This starts the same backend on port `8345` and opens a native window instead of a browser tab.

## Where to go next

- [[Repository Tour]] — what lives where, and why the project uses Bun and `uv`
- [[Architecture]] — how the frontend, backend, and hardware actually talk to each other
- [[Building and Packaging]] — building the frontend, packaging the backend, cutting a release
- [[Adding a Module]] — adding support for a new hardware module
- [[Troubleshooting]] — when one of the steps above does not go as described
