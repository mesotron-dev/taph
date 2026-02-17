# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- setup tools subpackage
- validation_tools module created
- Defined is_valid_slot function for dynamic __slots__ creation.
- Defined canonical_slots function for dynamic __slots__ creation.
- Added the protocols module with Freeze and Freezable protocols.

### Changed
- Update ruff and sync uv.lock
- Update librt v0.8.0 -> v0.8.1 & uv.lock

## [0.1.2] - 2026-02-12
### Fixed
- Fixed a defect where defining methods (`def`), `@staticmethod`, `@classmethod`, or `@property` on an `Immutable` or `Namespace` class would raise an `ImmutableError`.
- `freeze()` update to identify and permit functions and descriptors to pass through, enabling behavior to be defined alongside immutable state.

## [0.1.1] - 2026-2-11
### Fixed
- fixed & added classifiers for pyproject.toml
- minor fixes in readme

## [0.1.0] - 2026-02-11
### Added
- uv.lock for release
- Integrated automated testing and linting via GitHub Actions.
- py.typed version commit
- Update & lint for pyproject.toml
- Achieved 100% MC/DC test coverage for core immutability logic.
- Added test fixtures for dynamic class creation and validation.
- Verified protection against attribute mangling and deletion.
- `Immutable` base class for static instances.
- `Namespace` metaclass for static constants.
- `freeze` utility for recursive immutability.
- `ImmutableType` metaclass for `__slots__` enforcement.
- `TaphError` base exception.
- `ImmutableError` for specific immutability violations (inherits `TypeError`)

### Changed
- Update README to be release context aware
- Fix CI for releases
- Updates package `__init__` to expose public API.
- Update package version in `__init__`
- Update links and minor text lint for README.md

## [0.0.1] - 2026-02-09
### Added
- Initial project skeleton
- CHANGELOG.md
- Project configuration in pyproject.toml
- README.md
- LICENSE (Apache 2.0)
- SECURITY.md
