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

- The backend no longer defines its own state models. `SystemState`, the
  per-module states and the addon states now come from `dbay.state` (client
  0.6.0), so the GUI and any Python client validate against one schema instead
  of parallel copies that could drift. Which modules are valid remains a
  backend concern: `module_registry` feeds `build_system_state_model()`.
- A module type absent from the registry now validates as
  `dbay.state.UnknownModuleState` rather than failing the whole snapshot.
- `backend/modules/*_spec.py` renamed to `*_controller.py`, which is what they
  hold now that the state models have moved out. The split from the command
  modules stays — it breaks a real import cycle
  (`sync` → `initialize` → `module_registry`).
- No user-visible change: the sync wire format is unchanged, and the frontend's
  generated `interface.ts` still gets `ChSourceState`, `IVsourceAddon`,
  `ChSenseState`, `IVsenseAddon`, `VsourceChange` and `SharedVsourceChange`
  from `backend/addons/`, which re-export them.

### Fixed

- PyInstaller `hiddenimports` referenced `dbay.http`, removed when the client
  moved to lab-link websocket sync. Replaced with `dbay.gui_sync`, and
  `dbay.addons.vsense` added.

## [0.2.0] - 2026-06-16

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
