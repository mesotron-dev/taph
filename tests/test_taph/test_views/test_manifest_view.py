"""Tests for Manifest views providing comprehensive coverage using fixtures."""

import pytest
from taph.manifest import Manifest
from taph.views.manifest_views import (
    ManifestItemsView,
    ManifestKeysView,
    ManifestValuesView,
)


class EmptyConfig(Manifest):
    """Empty Manifest container for testing extreme layout boundaries."""

    __slots__ = ()


def test_keys_view_len_and_iter(system_manifest) -> None:
    """Verify standard length and iteration of the Manifest keys view."""
    keys = system_manifest.keys()
    assert isinstance(keys, ManifestKeysView)
    assert len(keys) == 3
    assert list(keys) == ['debug', 'timeout', 'version']


def test_keys_view_contains(system_manifest) -> None:
    """Exhaustive coverage for KeysView.__contains__."""
    keys = system_manifest.keys()

    assert 42 not in keys
    assert 'debug' in keys
    assert 'port' not in keys


def test_keys_view_comparisons_and_equality(system_manifest) -> None:
    """Validate set-like comparisons and equality constraints."""
    keys = system_manifest.keys()

    assert keys == {'debug', 'timeout', 'version'}
    assert keys != {'debug', 'timeout'}
    assert keys != {'debug', 'timeout', 'port'}
    assert keys.__eq__(42) is NotImplemented

    assert keys <= {'debug', 'timeout', 'version', 'port'}
    assert keys <= {'debug', 'timeout', 'version'}
    assert not (keys <= {'debug', 'timeout'})

    assert keys < {'debug', 'timeout', 'version', 'port'}
    assert not (keys < {'debug', 'timeout', 'version'})

    assert keys >= {'debug', 'timeout'}
    assert keys >= {'debug', 'timeout', 'version'}
    assert not (keys >= {'debug', 'timeout', 'port'})

    assert keys > {'debug', 'timeout'}
    assert not (keys > {'debug', 'timeout', 'version'})


def test_keys_view_set_operators(system_manifest) -> None:
    """Exhaustively cover binary operations on keys view."""
    keys = system_manifest.keys()

    assert keys & {'debug', 'port'} == {'debug'}
    assert {'debug', 'port'} & keys == {'debug'}

    assert keys | {'port'} == {'debug', 'timeout', 'version', 'port'}
    assert {'port'} | keys == {'debug', 'timeout', 'version', 'port'}

    assert keys - {'debug'} == {'timeout', 'version'}
    assert {'debug', 'port'} - keys == {'port'}

    assert keys ^ {'debug', 'port'} == {'timeout', 'version', 'port'}
    assert {'debug', 'port'} ^ keys == {'timeout', 'version', 'port'}

    assert keys.isdisjoint({'port', 'host'}) is True
    assert keys.isdisjoint({'debug', 'port'}) is False


def test_keys_view_hash(system_manifest) -> None:
    """Verify that hashing is stable and content-based."""
    keys = system_manifest.keys()
    assert isinstance(hash(keys), int)


def test_items_view_len_and_iter(system_manifest) -> None:
    """Verify structural view properties of the ItemsView."""
    items = system_manifest.items()
    assert isinstance(items, ManifestItemsView)
    assert len(items) == 3
    assert list(items) == [('debug', True), ('timeout', 90), ('version', '2.0.0')]


def test_items_view_contains(system_manifest) -> None:
    """Verify ItemsView.__contains__."""
    items = system_manifest.items()

    assert 'debug' not in items
    assert ('debug',) not in items
    assert ('debug', True, 'extra') not in items
    assert ('port', 8080) not in items
    assert ('debug', False) not in items
    assert ('debug', True) in items


def test_items_view_equality(system_manifest) -> None:
    """Test structural equality of the ItemsView."""
    items = system_manifest.items()

    assert items.__eq__(42) is NotImplemented
    assert items == {('debug', True), ('timeout', 90), ('version', '2.0.0')}
    assert items != {('debug', True), ('timeout', 90)}
    assert items != {('debug', True), ('timeout', 90), ('version', '3.0.0')}


def test_items_view_hash(system_manifest) -> None:
    """Verify items view produces a stable hash."""
    items = system_manifest.items()
    assert isinstance(hash(items), int)


def test_values_view_methods(system_manifest) -> None:
    """Verify standard sequence-like properties of ValuesView."""
    values = system_manifest.values()
    assert isinstance(values, ManifestValuesView)
    assert len(values) == 3
    assert list(values) == [True, 90, '2.0.0']

    assert True in values
    assert '2.0.0' in values
    assert '3.0.0' not in values

    expected = {'debug': True, 'timeout': 90, 'version': '2.0.0'}.values()
    assert values == expected
    assert values != {'debug': True, 'timeout': 90}.values()
    assert values != {'debug': True, 'timeout': 90, 'version': '3.0.0'}.values()
    assert values.__eq__(42) is NotImplemented
    assert isinstance(hash(values), int)


def test_nested_manifest_properties(user_manifest, system_manifest, sample_record) -> None:
    """Verify structural views on nested Manifest elements and Records."""
    keys = user_manifest.keys()
    items = user_manifest.items()
    values = user_manifest.values()

    assert len(keys) == 2
    assert list(keys) == ['config', 'user']
    assert list(items) == [('config', system_manifest), ('user', sample_record)]
    assert list(values) == [system_manifest, sample_record]


def test_empty_manifest_view_boundaries() -> None:
    """Verify empty Manifest edge cases for all three views."""
    assert len(EmptyConfig.keys()) == 0
    assert len(EmptyConfig.items()) == 0
    assert len(EmptyConfig.values()) == 0

    assert list(EmptyConfig.keys()) == []
    assert list(EmptyConfig.items()) == []
    assert list(EmptyConfig.values()) == []

    assert 'any' not in EmptyConfig.keys()
    assert ('any', 1) not in EmptyConfig.items()
    assert 1 not in EmptyConfig.values()
