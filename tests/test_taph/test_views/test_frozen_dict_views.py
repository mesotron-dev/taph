"""Tests for FrozenDict views providing comprehensive coverage."""

import bisect
import pytest
from taph.frozen_dict import FrozenDict
from taph.views.frozen_dict_views import (
    FrozenDictItemsView,
    FrozenDictKeysView,
    FrozenDictValuesView,
)


def test_keys_view_len_and_iter(sample_frozen_dict) -> None:
    """Verify standard length and iteration of the FrozenDict keys view."""
    keys = sample_frozen_dict.keys()
    assert isinstance(keys, FrozenDictKeysView)
    assert len(keys) == 3
    assert list(keys) == ['alpha', 'beta', 'gamma']


def test_keys_view_contains(sample_frozen_dict) -> None:
    """Exhaustive coverage for KeysView.__contains__."""
    keys = sample_frozen_dict.keys()

    assert 'alpha' in keys
    assert 'omega' not in keys
    assert 'delta' not in keys


def test_keys_view_contains_hash_collision(monkeypatch) -> None:
    """Simulate a hash collision to test collision branch resolution."""

    import taph.views.frozen_dict_views

    fd = FrozenDict({'collision1': 100})
    keys = fd.keys()

    original_mk_digest = taph.views.frozen_dict_views.mk_digest

    def mock_mk_digest(key: object) -> bytes:
        if key == 'collision2':
            return original_mk_digest('collision1')
        return original_mk_digest(key)

    monkeypatch.setattr(taph.views.frozen_dict_views, 'mk_digest', mock_mk_digest)

    assert 'collision1' in keys
    assert 'collision2' not in keys
    assert 'collision3' not in keys


def test_keys_view_comparisons_and_equality(sample_frozen_dict) -> None:
    """Validate set-like comparisons and equality constraints."""
    keys = sample_frozen_dict.keys()

    assert keys == {'alpha', 'beta', 'gamma'}
    assert keys != {'alpha', 'beta'}
    assert keys != {'alpha', 'beta', 'delta'}
    assert keys.__eq__(42) is NotImplemented

    assert keys <= {'alpha', 'beta', 'gamma', 'delta'}
    assert keys <= {'alpha', 'beta', 'gamma'}
    assert not (keys <= {'alpha', 'beta'})

    assert keys < {'alpha', 'beta', 'gamma', 'delta'}
    assert not (keys < {'alpha', 'beta', 'gamma'})

    assert keys >= {'alpha', 'beta'}
    assert keys >= {'alpha', 'beta', 'gamma'}
    assert not (keys >= {'alpha', 'beta', 'delta'})

    assert keys > {'alpha', 'beta'}
    assert not (keys > {'alpha', 'beta', 'gamma'})


def test_keys_view_set_operators(sample_frozen_dict) -> None:
    """Exhaustively cover binary operations on keys view."""
    keys = sample_frozen_dict.keys()

    assert keys & {'alpha', 'delta'} == {'alpha'}
    assert {'alpha', 'delta'} & keys == {'alpha'}

    assert keys | {'delta'} == {'alpha', 'beta', 'gamma', 'delta'}
    assert {'delta'} | keys == {'alpha', 'beta', 'gamma', 'delta'}

    assert {'alpha', 'delta'} - keys == {'delta'}

    assert keys ^ {'alpha', 'delta'} == {'beta', 'gamma', 'delta'}
    assert {'alpha', 'delta'} ^ keys == {'beta', 'gamma', 'delta'}

    assert keys.isdisjoint({'delta', 'epsilon'}) is True
    assert keys.isdisjoint({'alpha', 'delta'}) is False


def test_keys_view_hash(sample_frozen_dict) -> None:
    """Verify that hashing is stable and content-based."""
    keys = sample_frozen_dict.keys()
    assert isinstance(hash(keys), int)


def test_items_view_len_and_iter(sample_frozen_dict) -> None:
    """Verify structural view properties of the ItemsView."""
    items = sample_frozen_dict.items()
    assert isinstance(items, FrozenDictItemsView)
    assert len(items) == 3
    assert list(items) == [('alpha', 1), ('beta', 2), ('gamma', 3)]


def test_items_view_contains(sample_frozen_dict) -> None:
    """Verify ItemsView.__contains__."""
    items = sample_frozen_dict.items()

    assert 'alpha' not in items
    assert ('alpha',) not in items
    assert ('alpha', 1, 'extra') not in items
    assert ('delta', 4) not in items
    assert ('alpha', 99) not in items
    assert ('alpha', 1) in items


def test_items_view_equality(sample_frozen_dict) -> None:
    """Test structural equality of the ItemsView."""
    items = sample_frozen_dict.items()

    assert items.__eq__(42) is NotImplemented
    assert items == {'alpha': 1, 'beta': 2, 'gamma': 3}.items()
    assert items != {'alpha': 1, 'beta': 2}.items()
    assert items != {'alpha': 1, 'beta': 2, 'gamma': 99}.items()


def test_items_view_hash(sample_frozen_dict) -> None:
    """Verify items view produces a stable hash."""
    items = sample_frozen_dict.items()
    assert isinstance(hash(items), int)


def test_values_view_methods(sample_frozen_dict) -> None:
    """Verify standard sequence-like properties of ValuesView."""
    values = sample_frozen_dict.values()
    assert isinstance(values, FrozenDictValuesView)
    assert len(values) == 3
    assert list(values) == [1, 2, 3]

    assert 1 in values
    assert 99 not in values
    assert values == {'alpha': 1, 'beta': 2, 'gamma': 3}.values()
    assert values != {'alpha': 1, 'beta': 2}.values()
    assert values != {'alpha': 1, 'beta': 2, 'gamma': 99}.values()
    assert values.__eq__(42) is NotImplemented
    assert isinstance(hash(values), int)


def test_empty_dict_view_boundaries() -> None:
    """Verify empty dictionary edge cases for all three views."""
    empty_fd = FrozenDict()

    assert len(empty_fd.keys()) == 0
    assert len(empty_fd.items()) == 0
    assert len(empty_fd.values()) == 0

    assert list(empty_fd.keys()) == []
    assert list(empty_fd.items()) == []
    assert list(empty_fd.values()) == []

    assert 'any' not in empty_fd.keys()
    assert ('any', 1) not in empty_fd.items()
    assert 1 not in empty_fd.values()


def test_keys_view_isdisjoint_explicit(sample_frozen_dict) -> None:
    """Verify keys view behaves accurately with disjoint sets."""
    keys = sample_frozen_dict.keys()
    assert keys.isdisjoint(['delta', 'epsilon']) is True
    assert keys.isdisjoint(['alpha']) is False


def test_keys_view_hash_explicit(sample_frozen_dict) -> None:
    """Verify keys view stable-ID generation conforms to hash requirements."""
    keys = sample_frozen_dict.keys()
    assert isinstance(hash(keys), int)


def test_items_view_iterator_exhaustion_explicit(sample_frozen_dict):
    """Explicitly exhaust the items view iterator to cover the generator pipeline."""
    items = sample_frozen_dict.items()
    iterator = iter(items)

    assert next(iterator) == ('alpha', 1)
    assert next(iterator) == ('beta', 2)
    assert next(iterator) == ('gamma', 3)

    with pytest.raises(StopIteration):
        next(iterator)


def test_frozen_dict_keys_view_sub() -> None:
    """Verify that subtracting an iterable from a view works correctly."""
    fd = FrozenDict({'a': 1, 'b': 2, 'c': 3})
    keys_view = fd.keys()

    diff_set = keys_view - {'b', 'd'}
    assert diff_set == {'a', 'c'}

    diff_list = keys_view - ['a']
    assert diff_list == {'b', 'c'}
