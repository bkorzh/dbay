# Changelog

All notable changes to the `dbay` client (PyPI) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries accumulate under `## [Unreleased]`; `scripts/release.ts` stamps that
section with the version and date on each release.

## [Unreleased]

### Changed

- Require `lab-link>=0.3.0` (was `>=0.2.0`). The client uses the
  protocol-stable `LabLinkClient`, so no API changes were needed; the floor is
  raised to keep the whole project on a single lab-link line.
