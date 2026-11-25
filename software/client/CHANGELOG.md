# Changelog

All notable changes to the `dbay` client (PyPI) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries accumulate under `## [Unreleased]`; `scripts/release.ts` stamps that
section with the version and date on each release.

## [Unreleased]

## [0.6.0] - 2026-07-28

### Added

- `dbay.state` now holds the **full rack state schema** — `SystemState`, the
  per-module states (`Dac4DState`, `Dac16DState`, `Adc4DState`, `EmptyState`),
  the addon states (`ChSourceState`, `IVsourceAddon`, `ChSenseState`,
  `IVsenseAddon`, `PollingState`), and `Core` / `ModuleState`. The GUI backend
  imports these instead of defining its own, so client and server validate
  against one definition rather than three parallel copies that could drift.
- `UnknownModuleState`: a module type this build doesn't recognize no longer
  fails validation of the whole snapshot. It validates into this fallback with
  `core` typed and every other field preserved verbatim, so a consumer running
  an older build than the rack still sees the slots it does understand. A
  *malformed* module still raises — the fallback is for unknown modules, not
  invalid ones.
- `build_system_state_model(*extra_module_states)`: builds a `SystemState`
  whose module union also accepts custom modules. Which modules are valid is a
  backend concern (it has a plugin registry), so the backend calls this with
  its registry while plain consumers use `SystemState`. Raises a direct
  `TypeError` if a module's `module_type` is not a `Literal`, rather than
  letting pydantic fail from inside union construction.

### Changed

- State models now subclass `lab_link.ReactiveModel` rather than `BaseModel`.
  On the backend, assignments emit patch operations; off it, the node is not
  part of a bound state tree, so writes are simply not recorded and the model
  behaves as an ordinary validating pydantic model. One class serves both sides.
  **Potentially breaking**: a model nested inside one of these must now also
  subclass `ReactiveModel` — lab-link rejects a plain `BaseModel` child rather
  than silently losing reactivity.
- `dbay.addons.vsource` and `dbay.addons.vsense` are now the single definition
  of both the addon state models (re-exported from `dbay.state`) and the
  command payloads `VsourceChange`, `SharedVsourceChange` and `VsenseChange`.
  The GUI backend re-exports all of them rather than defining its own copies.
- `Dac4DPartialState` / `Dac16DPartialState` describe a module as a *direct
  mode* client sees it, where there is no GUI server and the addon state may be
  absent. `dbay.modules.dac4d.dac4D_spec` and `dbay.modules.dac16d.dac16D_spec`
  are now aliases of these rather than separate declarations, so the loose
  direct-mode shape is defined once alongside the strict one. `dac16D`'s `vsb`
  and `vr` gain real types (`ChSourceState` / `ChSenseState`) instead of `dict`.
- `IModule` and `Empty` remain as aliases for `ModuleState` and `EmptyState`.

## [0.5.0] - 2026-07-28

### Added

- `DBayClient.on_patch()` and `DBayClient.on_snapshot()`: public subscriptions to
  the GUI server's state broadcasts, so a consumer can keep a derived view live
  instead of polling `snapshot()`. Both connect the sync transport on demand
  (so they work with `load_state=False`) and return an unsubscribe callable.
  Previously the underlying lab-link callbacks were reachable only by going
  through `client._sync._client`.
- `DBayClient.state_version`: the version of the state the client currently
  holds, bumped on every applied patch. Lets a consumer cache a derived view and
  revalidate only when it changes, and detect a dropped update by comparing
  against the last version it saw.
- `GuiSync.on_patch()`, `GuiSync.on_snapshot()`, and `GuiSync.version` — the
  passthroughs the above are built on.

Note that the client applies each incoming patch to its own snapshot *before*
invoking callbacks, so subscribers never apply patch operations themselves;
re-reading `snapshot()` in the callback is sufficient. `PatchEvent.origin_client_id`
identifies which client's command produced a change, so a subscriber can ignore
echoes of its own writes.

## [0.4.1] - 2026-07-02

### Fixed

- `ADC4D.CORE_TYPE` is now `"adc4D"` (was `"ADC4D"`), matching the GUI/state
  `core.type` convention used by `dac4D`/`dac16D` and the websocket snapshot.
  `CORE_TYPE` is a state-identity label, not a wire-protocol name — the all-caps
  `ADC4D` firmware commands (`SETDEV`, `ADC4D VRD …`) are unchanged. This lets
  consumers match the module type exactly without case normalization.

## [0.4.0] - 2026-07-02

### Added

- `DBayClient.snapshot()` and `DBayClient.present_modules()`: public read-only
  accessors for the GUI server state. `present_modules()` returns `(slot, type)`
  pairs for discovery, so callers no longer need to reach into `GuiSync` or the
  underlying transport to enumerate installed modules. Both connect the sync
  transport on demand, so they work with `load_state=False`.

## [0.3.1] - 2026-06-16

### Changed

- Require `lab-link>=0.3.0` (was `>=0.2.0`). The client uses the
  protocol-stable `LabLinkClient`, so no API changes were needed; the floor is
  raised to keep the whole project on a single lab-link line.
