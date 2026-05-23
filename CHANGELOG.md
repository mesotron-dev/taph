# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-22
### Added
- Setup tools subpackage.
- `validation_tools` module (`is_valid_slot`, `canonical_slots`).
- Added the protocols module with Freeze and Freezable protocols.
- Added ThawError to exceptions module.
- Protocols module with `Freezable`, `Thawable`, and `Immutable` protocols.
- `ThawError` exception.
- Configuration subpackage.
- Added the test modules and config.
- Full support for core classes: `Record`, `Manifest`, and `FrozenDict` (with metaclasses and views).

### Changed
- Major refactoring: split monolithic core into focused modules and subpackages (`record`, `manifest`, `frozen_dict`, `meta/`, `views/`, `tools/`, `config/`).
- Updated Ruff linting configuration and ruleset.
- Increased Ruff `max-statements` limit to 25.
- Updated development dependencies (Ruff, Coverage, MyPy, etc.).
- Improved documentation and type hints.
- Updated the README. 

### Fixed
- Achieved **100% line and branch coverage**.
- Fixed `ValueError` when using `tuple.index()` in lookup paths.
- Improved `namespace_skip` to properly handle classes in nested namespaces.
- Removed multiple unreachable code blocks.
- Micro-optimized and reduced branching logic.
- Fixed manifest fixtures, meta configuration typo, and various edge cases.
- Minor documentation fixes.
- Completed _check_number and related tests

### Refactored
- Explicit `__init__` compilation and class construction overrides in `RecordType` metaclass.
- Streamlined internal APIs and reduced complexity in hash/freeze tools.
- Sorted `__all__` terms in exceptions module.
- General code cleanup, formatting, and test updates.

### Removed
- Removed legacy tests and refactored core module into new structure.

## [0.1.2] - 2026-02-12
### Fixed
- Fixed a defect where defining methods (`def`), `@staticmethod`, `@classmethod`, or `@property` on an `Immutable` or `Namespace` class would raise an `ImmutableError`.
- `freeze()` update to identify and permit functions and descriptors to pass through, enabling behavior to be defined alongside immutable state.

## [0.1.1] - 2026-2-11
### Fixed
- Fixed and added classifiers for `pyproject.toml`.
- Minor fixes in README.

## [0.1.0] - 2026-02-11
### Added
- uv.lock for release.
- Integrated automated testing and linting via GitHub Actions.
- `py.typed` version commit.
- 100% MC/DC test coverage for core immutability logic.
- `Immutable` base class and `ImmutableType` metaclass.
- `Namespace` metaclass for static constants.
- `freeze` utility.
- `TaphError` and `ImmutableError`.

### Changed
- Updated README and package metadata.
- Exposed public API in `__init__`.

## [0.0.1] - 2026-02-09
### Added
- Initial project skeleton.
- CHANGELOG.md, pyproject.toml, README.md.
- LICENSE (Apache 2.0) and SECURITY.md.
