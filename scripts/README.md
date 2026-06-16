# Release Scripts

This folder contains release helpers for version bumping, changelog stamping,
and git tagging.

## Scripts

- `release.ts`: bumps versions, stamps the changelog, and creates namespaced tags.
- `extract_changelog.py`: prints one version's changelog section; used by the
  release workflows to fill the GitHub Release body.

## Usage

Run from repository root:

```bash
bun scripts/release.ts <target> <bump> [options]
```

- `<target>`: `gui` or `client`
- `<bump>`: `patch`, `minor`, or `major`

## Examples

Preview next GUI release (no changes):

```bash
bun scripts/release.ts gui patch --dry-run
```

Create GUI release commit + tag:

```bash
bun scripts/release.ts gui patch
git push origin HEAD
git push origin gui-vX.Y.Z
```

Create and push GUI release in one command:

```bash
bun scripts/release.ts gui patch --push
```

Preview next Python client release:

```bash
bun scripts/release.ts client patch --dry-run
```

Create and push Python client release:

```bash
bun scripts/release.ts client patch --push
```

## Changelog workflow

Release notes are **not** written by hand on GitHub anymore. Each target keeps a
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) file:

- GUI: `software/gui/CHANGELOG.md`
- Python client: `software/client/CHANGELOG.md`

Add notes for in-progress work under the `## [Unreleased]` heading as you go. On
release, `release.ts` rewrites `## [Unreleased]` into a dated `## [X.Y.Z]`
section (leaving a fresh, empty Unreleased above it) and includes the file in the
release commit. The release CI then runs `extract_changelog.py` to pull that
section into the GitHub Release body — for both the GUI (`tauri_release.yml`)
and the Python client (`publish_pypi.yml`).

If the version being released has no changelog section, CI fails rather than
shipping empty notes, so keep the Unreleased section current.

## What gets bumped

- `gui`: `tauri.conf.json`, `Cargo.toml`, **and `Cargo.lock`** (the local crate's
  own `[[package]]` version, kept in step automatically), the changelog, **and
  `software/gui/backend/uv.lock`** — the backend bundles the `dbay` client as an
  editable path dependency, so the script re-runs `uv lock` to pick up the
  current client version (the Tauri build runs `uv sync --locked` and would
  otherwise fail). This requires `uv` on PATH when cutting a GUI release.
- `client`: `pyproject.toml` plus the changelog.

## Tag format

- GUI tags: `gui-vX.Y.Z`
- Python client tags: `py-vX.Y.Z`

Pushing a `gui-vX.Y.Z` tag triggers the Tauri build + GitHub release workflow;
pushing a `py-vX.Y.Z` tag triggers the PyPI publish + GitHub release workflow.

## Options

- `--dry-run`: show planned version/tag without changing files
- `--no-commit`: update version files only; do not commit or tag
- `--push`: push commit and tag to `origin`
- `--allow-dirty`: allow running with local uncommitted changes
