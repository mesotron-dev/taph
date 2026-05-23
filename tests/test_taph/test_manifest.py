"""Tests for the taph.manifest module."""

import sys
import pytest
from taph.manifest import Manifest
from taph.exceptions import ManifestError, ImmutableError

class AppConfig(Manifest):
    __slots__ = ()
    VERSION = "1.0.0"
    DEBUG = False
    PORT = 8080

def test_manifest_class_attributes():
    """Verify properties are accessible at the class level."""
    assert AppConfig.VERSION == "1.0.0"
    assert AppConfig.DEBUG is False
    assert AppConfig.get('PORT') == 8080
    assert AppConfig.get('MISSING', "fallback") == "fallback"

def test_manifest_instantiation_blocked():
    """Verify Manifest cannot be instantiated."""
    with pytest.raises(AttributeError, match="A Manifest has no instances"):
        _ = AppConfig()

def test_manifest_immutability():
    """Verify class-level attribute locks."""
    with pytest.raises(ImmutableError):
        AppConfig.DEBUG = True

    with pytest.raises(ImmutableError):
        del AppConfig.PORT

def test_manifest_blocked_mutations() -> None:
    """Verify dictionary-like mutations raise ManifestError."""
    with pytest.raises(ManifestError):
        AppConfig.pop('PORT')
    with pytest.raises(ManifestError):
        AppConfig.popitem()
    with pytest.raises(ManifestError):
        AppConfig.clear()
    with pytest.raises(ManifestError):
        AppConfig.update({'DEBUG': True})
    with pytest.raises(ManifestError):
        AppConfig.setdefault('DEBUG', True)

def test_manifest_views():
    """Verify class-level views."""
    keys = list(AppConfig.keys())
    assert "VERSION" in keys
    assert "DEBUG" in keys
    assert "PORT" in keys
    assert len(AppConfig) == 3


def test_manifest_metaclass_operations() -> None:
    """Verify structural dunder operations implemented on ManifestType."""
    assert "PORT" in AppConfig
    assert "MISSING" not in AppConfig
    assert 999 not in AppConfig  # type: ignore[operator]

    assert AppConfig["PORT"] == 8080
    with pytest.raises(KeyError):
        _ = AppConfig["MISSING"]

    items = dict(AppConfig)  # iterates over zip(keys, values)
    assert items["PORT"] == 8080
    assert len(AppConfig) == 3

    assert isinstance(AppConfig.fingerprint, str)
    assert isinstance(AppConfig.hexdigest, str)
    assert sys.getsizeof(AppConfig) > 0

    class IdenticalConfig(Manifest):
        __slots__ = ()
        VERSION = "1.0.0"
        DEBUG = False
        PORT = 8080

    class DifferentConfig(Manifest):
        __slots__ = ()
        VERSION = "2.0.0"

    assert AppConfig == IdenticalConfig
    assert AppConfig != DifferentConfig
    assert AppConfig != "unrelated_type"

    with pytest.raises(TypeError):
        _ = AppConfig | 123

    with pytest.raises(TypeError):
        _ = 123 | AppConfig


def test_manifest_copy() -> None:
    """Verify the copy method returns the immutable class itself."""
    assert AppConfig.copy() is AppConfig


def test_manifest_metaclass_repr() -> None:
    """Verify the metaclass __repr__ outputs descriptive structural details."""
    representation = repr(AppConfig)
    assert "length:" in representation
    assert "VERSION" in representation


def test_manifest_ne_and_eq_comprehensive() -> None:
    """Verify all class-level comparisons and equality checks."""
    class M1(Manifest):
        __slots__ = ()
        X = 1

    class M2(Manifest):
        __slots__ = ()
        X = 1

    class M3(Manifest):
        __slots__ = ()
        X = 2

    assert M1 == M2
    assert not (M1 == M3)
    assert M1 != M3
    assert not (M1 != M2)
    assert (M1 == 123) is False
    assert (M1 != 123) is True
