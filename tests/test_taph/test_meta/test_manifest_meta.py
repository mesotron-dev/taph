"""Tests for the taph.meta.manifest_meta module (ManifestType)."""

import sys
import pytest
from collections.abc import Mapping
from taph.manifest import Manifest
from taph.meta.manifest_meta import ManifestType, _parse_namespace
from taph.exceptions import ManifestError


class SampleManifest(Manifest):
    """Test Manifest containing constant state parameters."""

    __slots__ = ()
    PORT = 443
    SYSTEM = "production"


def test_parse_namespace_filtering() -> None:
    """Verify that dunders, callables, and special internal definitions are excluded."""
    namespace = {
        "__dunder__": "skip",
        "_abc_impl": "skip",
        "method_a": lambda x: x,
        "PORT": 80,
        "ENVIRONMENT": "test"
    }
    keys, values, digest = _parse_namespace(namespace)
    assert "PORT" in keys
    assert "ENVIRONMENT" in keys
    assert "__dunder__" not in keys
    assert "method_a" not in keys
    assert isinstance(digest, bytes)


def test_parse_namespace_empty() -> None:
    """Verify boundary condition for parsing an empty dictionary namespace."""
    keys, values, digest = _parse_namespace({})
    assert keys == ()
    assert values == ()
    assert isinstance(digest, bytes)


def test_manifest_type_new_slots_mcdc() -> None:
    """Verify __slots__ checking constraints on Class template creation."""
    class AutoSlots(metaclass=ManifestType):
        CONST = 100
    assert AutoSlots.__slots__ == ()

    class ExplicitSlots(metaclass=ManifestType):
        __slots__ = ()
        CONST = 200
    assert ExplicitSlots.__slots__ == ()

    with pytest.raises(AttributeError, match="A Manifest has no instances"):
        class BadSlots(metaclass=ManifestType):
            __slots__ = ('leaked_field',)


def test_manifest_type_mapping_protocol_operators() -> None:
    """Verify read-only container dictionary interfaces."""
    assert "PORT" in SampleManifest
    assert "MISSING" not in SampleManifest
    assert 999 not in SampleManifest  # Non-string key safety check

    assert len(SampleManifest) == 2
    assert SampleManifest["PORT"] == 443

    with pytest.raises(KeyError):
        _ = SampleManifest["MISSING"]

    assert isinstance(hash(SampleManifest), int)
    assert len(list(SampleManifest)) == 2

    assert isinstance(SampleManifest.fingerprint, str)
    assert isinstance(SampleManifest.hexdigest, str)

    assert isinstance(sys.getsizeof(SampleManifest), int)
    assert isinstance(ManifestType.__sizeof__(SampleManifest), int)


def test_manifest_type_equality_logic() -> None:
    """Verify structural content equality logic for Manifest constants."""
    class IdenticalManifest(Manifest):
        __slots__ = ()
        PORT = 443
        SYSTEM = "production"

    class DifferentManifest(Manifest):
        __slots__ = ()
        PORT = 80

    assert SampleManifest == IdenticalManifest
    assert SampleManifest != DifferentManifest
    assert SampleManifest != "unrelated_type"
    assert (SampleManifest == "unrelated_type") is False


def test_manifest_type_or_operators_mcdc() -> None:
    """MC/DC: Verify error handling on merge operations with other mapping types."""
    assert ManifestType.__or__(SampleManifest, 123) is NotImplemented
    assert ManifestType.__ror__(SampleManifest, 123) is NotImplemented

    with pytest.raises(TypeError):
        _ = SampleManifest | 123

    with pytest.raises(TypeError):
        _ = 123 | SampleManifest

    with pytest.raises(Exception):
        _ = SampleManifest | {"OVERWRITE": "val"}

    with pytest.raises(Exception):
        _ = {"OVERWRITE": "val"} | SampleManifest
