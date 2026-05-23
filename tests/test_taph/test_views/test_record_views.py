"""Tests for Record views providing comprehensive coverage."""

import pytest
from taph.record import Record
from taph.views.record_views import (
    RecordItemsView,
    RecordKeysView,
    RecordValuesView,
)


class EmptyRecord(Record):
    """Empty Record subclass for testing edge boundaries."""

    __slots__ = ()


def test_keys_view_len_and_iter(sample_record) -> None:
    """Verify standard length and iteration of the Record keys view."""
    keys = sample_record.keys()
    assert isinstance(keys, RecordKeysView)
    assert len(keys) == 3
    assert list(keys) == ['user_id', 'email', 'is_active']


def test_keys_view_contains(sample_record) -> None:
    """Exhaustive coverage for KeysView.__contains__."""
    keys = sample_record.keys()

    assert 123 not in keys
    assert 'user_id' in keys
    assert 'missing_key' not in keys


def test_keys_view_comparisons_and_equality(sample_record) -> None:
    """Validate set-like comparisons and equality constraints."""
    keys = sample_record.keys()

    assert keys == {'user_id', 'email', 'is_active'}
    assert keys != {'user_id', 'email'}
    assert keys != {'user_id', 'email', 'password'}
    assert keys.__eq__(123) is NotImplemented

    assert keys <= {'user_id', 'email', 'is_active', 'extra'}
    assert keys <= {'user_id', 'email', 'is_active'}
    assert not (keys <= {'user_id', 'email'})
    assert not (keys <= {'user_id', 'email', 'extra'})

    assert keys < {'user_id', 'email', 'is_active', 'extra'}
    assert not (keys < {'user_id', 'email', 'is_active'})
    assert not (keys < {'user_id', 'email'})
    assert not (keys < {'user_id', 'email', 'extra'})

    assert keys >= {'user_id', 'email'}
    assert keys >= {'user_id', 'email', 'is_active'}
    assert not (keys >= {'user_id', 'email', 'is_active', 'extra'})
    assert not (keys >= {'user_id', 'email', 'extra'})

    assert keys > {'user_id', 'email'}
    assert not (keys > {'user_id', 'email', 'is_active'})
    assert not (keys > {'user_id', 'email', 'is_active', 'extra'})
    assert not (keys > {'user_id', 'email', 'extra'})


def test_keys_view_set_operators(sample_record) -> None:
    """Exhaustively cover binary operations on keys view."""
    keys = sample_record.keys()

    assert keys & {'user_id', 'extra'} == {'user_id'}
    assert {'user_id', 'extra'} & keys == {'user_id'}

    assert keys | {'extra'} == {'user_id', 'email', 'is_active', 'extra'}
    assert {'extra'} | keys == {'user_id', 'email', 'is_active', 'extra'}

    assert keys - {'user_id'} == {'email', 'is_active'}
    assert {'user_id', 'extra'} - keys == {'extra'}

    assert keys ^ {'user_id', 'extra'} == {'email', 'is_active', 'extra'}
    assert {'user_id', 'extra'} ^ keys == {'email', 'is_active', 'extra'}

    assert keys.isdisjoint({'extra', 'none'}) is True
    assert keys.isdisjoint({'user_id', 'extra'}) is False


def test_keys_view_hash(sample_record) -> None:
    """Verify that hashing is stable and content-based."""
    keys1 = sample_record.keys()
    keys2 = sample_record.keys()
    assert hash(keys1) == hash(keys2)


def test_items_view_len_and_iter(sample_record) -> None:
    """Verify structural view properties of the ItemsView."""
    items = sample_record.items()
    assert isinstance(items, RecordItemsView)
    assert len(items) == 3
    assert list(items) == [('user_id', 101), ('email', 'arch@taph.io'), ('is_active', True)]


def test_items_view_contains(sample_record) -> None:
    """Verify ItemsView.__contains__."""
    items = sample_record.items()

    assert 'user_id' not in items
    assert ('user_id',) not in items
    assert ('user_id', 101, 'extra') not in items
    assert (123, 101) not in items
    assert ('missing_key', 101) not in items
    assert ('user_id', 101) in items
    assert ('user_id', 99) not in items


def test_items_view_equality(sample_record) -> None:
    """Test structural equality of the ItemsView."""
    items = sample_record.items()

    assert items.__eq__(123) is NotImplemented

    expected = {'user_id': 101, 'email': 'arch@taph.io', 'is_active': True}.items()
    assert items == expected
    assert items != {'user_id': 101, 'email': 'arch@taph.io'}.items()
    assert items != {'user_id': 101, 'email': 'arch@taph.io', 'is_active': False}.items()

def test_items_view_hash(sample_record) -> None:
    """Verify items view produces a stable hash."""
    items1 = sample_record.items()
    items2 = sample_record.items()
    assert hash(items1) == hash(items2)


def test_values_view_methods(sample_record) -> None:
    """Verify standard sequence-like properties of ValuesView."""
    values = sample_record.values()
    assert isinstance(values, RecordValuesView)
    assert len(values) == 3
    assert list(values) == [101, 'arch@taph.io', True]

    assert 101 in values
    assert 'arch@taph.io' in values
    assert 999 not in values

    expected = {'user_id': 101, 'email': 'arch@taph.io', 'is_active': True}.values()
    assert values == expected
    assert values != {'user_id': 101, 'email': 'arch@taph.io'}.values()
    assert values != {'user_id': 101, 'email': 'arch@taph.io', 'is_active': 'wrong_val'}.values()

    assert values.__eq__(123) is NotImplemented
    assert isinstance(hash(values), int)


def test_empty_record_view_boundaries() -> None:
    """Verify empty Record edge cases for all three views."""
    empty_rec = EmptyRecord()

    assert len(empty_rec.keys()) == 0
    assert len(empty_rec.items()) == 0
    assert len(empty_rec.values()) == 0

    assert list(empty_rec.keys()) == []
    assert list(empty_rec.items()) == []
    assert list(empty_rec.values()) == []

    assert 'any' not in empty_rec.keys()
    assert ('any', 1) not in empty_rec.items()
    assert 1 not in empty_rec.values()
