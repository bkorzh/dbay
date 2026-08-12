---
order: 6
---

# Troubleshooting

Problems that have actually come up, and what fixes them. If you have not set the project up yet, start at [[Start Here]].

Before working through anything below, run the diagnostic. It changes nothing, and it names most of these problems directly:

```bash
./setup.sh --check          # .\setup.ps1 --check on Windows
```

It reports your tool versions, whether the backend environment matches `uv.lock`, and whether `node_modules` matches `package.json` — including packages that are missing or older than required. Running `./setup.sh` without `--check` then fixes the environment problems it found.

## `Rollup failed to resolve import "lab-link/svelte"`

The full error looks like this:

```text
[vite]: Rollup failed to resolve import "lab-link/svelte" from
".../frontend/src/state/systemState.svelte.ts".
```

Your `node_modules` predates a dependency change. `node_modules` is not in Git, so a `git pull` that adds or bumps a package leaves the old install in place, and the import genuinely is not on disk.

```bash
cd software/gui/frontend
rm -rf node_modules
bun install
```

`./setup.sh --check` identifies this precisely, listing the missing and out-of-date packages. By hand, compare the vite version the build prints against the one in `package.json`: if the build says `vite v7.3.1` while `package.json` asks for `^7.3.5`, you are running an install from an older checkout.

The wrapper scripts (`build.sh`, `dev-browser.sh`, `dev-tauri.sh`) run `bun install` for you, so this normally only bites when calling `vite`, `bun run build`, or `bun run dev` directly.

## `Failed to spawn: fastapi` or `fastapi: command not found`

The backend used to be a FastAPI app and is now plain Starlette served by uvicorn; FastAPI is not a dependency any more. If something is still invoking `fastapi dev`, it is an old checkout or an old command. Pull the latest `main`, and start the backend with:

```bash
cd software/gui/backend
uv run uvicorn backend.main:app --port 8345 --host 0.0.0.0 --reload --reload-dir backend
```

## `bun` or `uv` not found

Restart your terminal first — both installers add to your shell profile. If the command is still missing, check the install location is on your `PATH` (`~/.bun/bin` and `~/.local/bin` respectively).

## `uv sync` cannot find a compatible Python

The backend needs Python `>=3.11,<3.14`:

```bash
uv python install 3.11
uv sync
```

## Port `8345` or `5173` already in use

Usually a dev server from an earlier session that did not shut down.

```bash
lsof -ti tcp:8345 tcp:5173        # macOS / Linux: list the offending PIDs
kill $(lsof -ti tcp:8345 tcp:5173)
```

On Windows, use `netstat -ano | findstr :8345` and `taskkill /PID <pid> /F`.

## The UI loads but stays empty

The page is served, but it never attached to the backend's state. Look for this line in the backend log:

```text
INFO:     127.0.0.1:51944 - "WebSocket /sync/ws" [accepted]
```

If it is missing, the frontend is not reaching `ws://127.0.0.1:8345/sync/ws`. Check that the backend process is actually running, that it is on port `8345`, and that nothing (a proxy, a VPN, a firewall prompt you dismissed) is blocking the local WebSocket. You can test the endpoint independently:

```bash
curl -i -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     http://127.0.0.1:8345/sync/ws
```

A healthy backend answers `101 Switching Protocols`.

## Blank page or missing assets when the backend serves the UI

The backend can only serve the UI from `software/gui/backend/backend/compiled_frontend/`, which is populated by the frontend build. If you started the backend on its own and opened port `8345` directly, build the frontend once:

```bash
./software/gui/build.sh frontend
```

During normal browser development you use Vite on port `5173` instead, and this does not apply.

## Yesterday's rack state came back

That is intentional: the backend persists state to SQLite in your user data directory. To start clean or keep dev runs out of your real state:

```bash
DBAY_PERSIST=0 ./software/gui/dev-browser.sh                    # no persistence
DBAY_PERSIST_DB=/tmp/dbay_dev.db ./software/gui/dev-browser.sh  # a throwaway database
```

Channel `activated` and `measuring` flags always reset on startup even when the rest is restored, because the software cannot know whether an output is live.

## Everything is slow, and nothing errors

If `dev_mode` is enabled in `software/gui/backend/backend/config/vsource_params.json` and there is no rack at the configured address, hardware requests wait for a UDP timeout. The symptom is a sluggish UI rather than a clear failure.

## Import errors when running `main.py`

`backend/main.py` imports its siblings as `backend.something`, so running it as a loose script from inside the package directory fails. Start it from the project root instead:

```bash
cd software/gui/backend
uv run uvicorn backend.main:app --port 8345 --host 0.0.0.0    # preferred
uv run python -m backend.main                                 # no auto-reload
```

## Tauri fails to start or build

Almost always missing Rust or missing native libraries — `bun install` does not provide either. Work through the optional Tauri section of [[Start Here]] and the [official prerequisites](https://v2.tauri.app/start/prerequisites) for your OS. A Tauri *build* additionally needs a packaged backend, so run `./software/gui/build.sh backend` first, or use `all`.

## The `.sh` scripts do not run on Windows

They are Bash scripts. Use Git Bash, or call the Bun scripts directly from `software/gui/frontend`: `bun run develop`, `bun run developtauri`, `bun run buildfrontend`, `bun run buildall`.

## When in doubt, reset

```bash
cd software/gui/frontend && rm -rf node_modules && bun install
cd ../backend && uv sync
cd ../frontend && bun ./build.ts --clean     # also clears Tauri and PyInstaller artifacts
```
