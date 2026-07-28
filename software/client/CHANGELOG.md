# Changelog

All notable changes to the `dbay` client (PyPI) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries accumulate under `## [Unreleased]`; `scripts/release.ts` stamps that
section with the version and date on each release.

## [Unreleased]

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
