# Release Scripts

This folder contains release helpers for version bumping and git tagging.

## Script

- `release.ts`: bumps versions and creates namespaced tags.

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

## Tag format

- GUI tags: `gui-vX.Y.Z`
- Python client tags: `py-vX.Y.Z`

Pushing a `gui-vX.Y.Z` tag triggers the Tauri build workflow automatically.

## Options

- `--dry-run`: show planned version/tag without changing files
- `--no-commit`: update version files only; do not commit or tag
- `--push`: push commit and tag to `origin`
- `--allow-dirty`: allow running with local uncommitted changes
