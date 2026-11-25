---
order: 4
---

# Building and Packaging

Everything release-shaped: compiling the frontend, packaging the backend, building installers, and cutting a release. For day-to-day development you do not need any of this — see [[Start Here]].

## The wrapper script

On macOS and Linux, from the repository root:

```bash
./software/gui/build.sh frontend   # build the UI into the backend's compiled_frontend/
./software/gui/build.sh backend    # package the backend with PyInstaller
./software/gui/build.sh tauri      # build the desktop installers
./software/gui/build.sh all        # all three, in order
```

On Windows, call the underlying Bun scripts:

```powershell
cd software/gui/frontend
bun run buildfrontend
bun run buildbackend
bun run buildtauri
bun run buildall
```

Both routes run the same orchestrator, `software/gui/frontend/build.ts`. The wrapper runs `bun install` first so the build cannot fail on a stale `node_modules`.

Two extra flags exist only on the orchestrator:

```bash
cd software/gui/frontend
bun ./build.ts --clean      # remove src-tauri/resources, src-tauri/target, and the backend dist/build dirs
bun ./build.ts --flatpak    # build a Flatpak bundle (Linux only, after a Tauri build)
```

## What each step actually does

### Frontend

`vite build`, then the compiled `assets/` and `index.html` are copied into:

```text
software/gui/backend/backend/compiled_frontend/
```

That directory is what lets the backend serve the UI on its own. It is **not in Git** — `index.html` references content-hashed asset filenames, so a committed copy would go stale on any code change and dirty the tree after every build. A fresh clone therefore has no compiled frontend, and a backend started outside the Vite workflow answers `/` with a short "the frontend has not been built" page instead. It still starts and still serves `/sync/ws`.

### Backend

PyInstaller runs inside the backend project:

```bash
uv run --project ./ pyinstaller backend/main.spec
```

The result is `software/gui/backend/dist/dbaybackend/`, containing the `dbaybackend` executable and its `device-bay_internal/` support directory. The build clears `dist/` and `build/` first so stale artifacts cannot leak into a release.

PyInstaller bundles `compiled_frontend/` wholesale, so packaging without building the frontend first would produce an installer with no interface. The `backend` target refuses to run in that case:

```text
>>>>> No compiled frontend to package.
Expected .../backend/compiled_frontend/index.html
Run the frontend build first:
  ./software/gui/build.sh frontend
```

The check runs before anything is deleted, so a failed run leaves an existing build alone. `all` is unaffected, since it builds the frontend first.

Because the executable bundles whatever is in the environment, packaging is only reproducible if the environment was created with `uv sync` — this is the main reason the project standardizes on `uv` (see [[Repository Tour]]).

### Tauri

The packaged backend is copied into `src-tauri/resources/` as a sidecar, then `tauri build` produces the installers. Three details worth knowing:

- on macOS and Linux the build launches the packaged backend for two seconds and kills it, which works around slow first-launch behaviour on Debian
- on Windows it generates `src-tauri/windows/fragments/frag.wxs` with machine-specific absolute paths, adding TCP and UDP firewall exceptions for the backend
- `TAURI_BUNDLE_TARGETS` narrows the bundle formats (`bun run tauri build --bundles …`), which is how CI builds one format per platform

A Tauri build expects a packaged backend to already exist, so run `backend` before `tauri`, or just use `all`.

### Flatpak

Linux only, and it runs after a Tauri build because it repackages the generated `.deb`. It copies `src-tauri/flatpak_resources/` into `src-tauri/flatpak/`, fills the `.deb` filename into the manifest template, then runs `flatpak-builder` and `flatpak build-bundle` to produce `device-bay.flatpak`.

## Tests

```bash
cd software/gui/backend && uv run pytest      # backend, including lab-link sync and polling tests
cd software/gui/frontend && bun run test      # frontend (vitest)
```

Neither needs hardware or a running server. The backend suite disables persistence through `conftest.py` so it never touches your real state database.

## Releases

Do not bump versions, write release notes, or build installers by hand. `scripts/release.ts` does the version arithmetic and tagging, and pushing the tag makes GitHub Actions build and publish everything.

There are two independently versioned things in this repository:

| Target | Versioned by | Tag | Result |
| --- | --- | --- | --- |
| `gui` | `src-tauri/tauri.conf.json` + `Cargo.toml` | `gui-vX.Y.Z` | desktop installers attached to a GitHub release |
| `client` | `software/client/pyproject.toml` | `py-vX.Y.Z` | the `dbay` package published to PyPI |

Both follow [semantic versioning](https://semver.org/spec/v2.0.0.html). While the GUI is pre-1.0, breaking changes bump the **minor** version.

### Keep the changelog current as you work

Release notes are never written on GitHub. Each target keeps a [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) file — `software/gui/CHANGELOG.md` and `software/client/CHANGELOG.md` — and you add entries under `## [Unreleased]` as part of the change that needs them, under `### Added`, `### Changed`, `### Fixed`.

At release time, `release.ts` rewrites `## [Unreleased]` into a dated `## [X.Y.Z]` section and opens a fresh empty `Unreleased` above it. CI then extracts that exact section with `scripts/extract_changelog.py` and uses it as the GitHub Release body. If the version has no changelog section, **CI fails rather than shipping empty notes** — so an out-of-date Unreleased section blocks the release.

### Cutting a release

Preview first; the script tells you the version it would pick and every file it would touch:

```bash
bun scripts/release.ts gui patch --dry-run
```

Then do it for real:

```bash
bun scripts/release.ts gui patch          # bump, stamp changelog, commit, tag
git push origin HEAD
git push origin gui-vX.Y.Z
```

Or in one step:

```bash
bun scripts/release.ts gui patch --push
```

Substitute `client` for `gui`, and `minor` or `major` for `patch`. The next version is computed from the higher of the version in the files and the highest existing tag, so it cannot silently reuse or skip a number.

The working tree must be clean unless you pass `--allow-dirty`, and `uv` must be on your `PATH` for a `gui` release. `--no-commit` updates the files and stops, if you want to inspect them before committing. Full option list: `scripts/README.md`, or `bun scripts/release.ts --help`.

### What a `gui` release changes

- `src-tauri/tauri.conf.json` and `src-tauri/Cargo.toml` — the app version
- `src-tauri/Cargo.lock` — the version on the local crate's own package entry, rewritten directly so no Rust toolchain or network access is needed
- `software/gui/backend/uv.lock` — re-locked with `uv lock`, because the backend depends on `software/client/` as an editable path dependency and the CI build runs `uv sync --locked`, which fails on a stale lockfile
- `software/gui/CHANGELOG.md` — stamped

A `client` release changes `pyproject.toml` and its changelog. If a change spans both, release the client as well so PyPI users get the same code the app ships.

Both then get a `release(<target>): <tag>` commit and an annotated tag.

### What CI does with the tag

Pushing `gui-vX.Y.Z` runs `Build Tauri release assets`:

1. validates that the tag matches `tauri.conf.json` and `Cargo.toml`
2. validates that `software/gui/CHANGELOG.md` has a section for that version
3. builds on macOS, Windows, and Linux with `uv sync --locked`, `bun install --frozen-lockfile`, and `bun run buildall`
4. builds the Flatpak bundle on Linux
5. creates the GitHub release with the changelog section as the body and the installers attached

Rust is pinned to `1.89.0` in CI. `workflow_dispatch` on the workflow builds without publishing, for testing the pipeline.

Pushing `py-vX.Y.Z` runs `Publish to PyPI`: it validates the tag against `software/client/pyproject.toml`, builds the package, publishes with trusted publishing, and creates the matching GitHub release from the changelog.

If a tag fails validation, delete it locally and remotely, fix the problem, and cut the release again — CI will not build a tag whose versions disagree with the repository.

### Documentation

Every push to `main` rebuilds the Quartz site from `docs/`. No tag, no version bump.

## Aliases in the backend

`software/gui/backend/backend/makefile` has `make build`, `make serve`, `make build-python`, `make build-tauri`, and `make build-all` targets. They only delegate to the scripts above, so there is no second copy of the build logic to keep in sync.
