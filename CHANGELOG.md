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
- Added ThawError to exceptions module.
- Added the config and test_config subpackages.

### Changed
- Update librt v0.8.0 -> v0.8.1 & uv.lock
- Update ruff v0.15.1 -> v0.15.2 & uv.lock
- Update exceptions module with new class names
- Update protocols module with the Immutable protocol
- Update taph.__init__ module with new names
- Update ruff v0.15.2 -> v0.15.4
- Update pyproject.tool.ruff.lint with more coverage and sorted list
- Update taph.protocols doc strings
- Update max statements to a more lenient 20 in pyproject.toml ruff lint
- Update ruff v0.15.4 -> v0.15.7
- Update coverage v7.13.4 -> v7.13.5
- Update project lock file
- Update protocols module with thaw protocols
- Update pygments v2.19.2 -> v2.20.0
- Update ruff v0.15.7 -> v0.15.8
- Update uv.log + ast-serialize==0.5.0
- Update coverage v7.13.5 -> v7.14.0
- Update librt v0.8.1 -> v0.11.0
- Update mypy v1.20.0 -> v2.1.0
- Update packaging v26.0 -> v26.2
- Update pathspec v1.0.4 -> v1.1.1
- Update pytest v9.0.2 -> v9.0.3
- Update ruff v0.15.9 -> v0.15.13

### Fixed
- minor doc fixes

### Refactored
- Sorted  __all__ terms in the exceptions module
- Minor code improvements and doc updates in the validation_tools module
- max statements for ruff now 25

### Removed
- Refactored core module and refactored into new classes & modules 

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
