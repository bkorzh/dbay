# Changelog

All notable changes to the Device Bay GUI (Tauri app + backend) are documented
in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While the GUI is pre-1.0, breaking changes bump the minor version.

Entries accumulate under `## [Unreleased]`; `scripts/release.ts` stamps that
section with the version and date on each release.

## [Unreleased]

### Changed

- **Breaking:** migrated the backend to lab-link 0.3.0's reactive state engine.
  All backend state models subclass `ReactiveModel` and are bound once via
  `sync.bind_state`, so every mutation is validated, batched per event-loop
  tick, and broadcast automatically. The manual publish-helper layer (the
  "split brain" between pydantic models and a separate wire dict) is removed.
- Replaced FastAPI with Starlette for serving the compiled SPA and the sync
  websocket. FastAPI is no longer a dependency; `uvicorn[standard]` is now a
  direct dependency.

### Added

- SQLite persistence via `lab-link[persist]`: module layout, channel names, and
  bias setpoints survive restarts. Transient flags (activated / measuring /
  polling) and live readings are reset on restore for hardware safety. Override
  the location with `DBAY_PERSIST_DB`; disable with `DBAY_PERSIST=0`.
