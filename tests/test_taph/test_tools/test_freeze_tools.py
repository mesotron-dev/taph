"""Tests for the taph.tools.freeze_tools module."""

from collections import deque
from collections.abc import Iterator, Mapping, Sequence
from typing import Any
import pytest

from taph.frozen_dict import FrozenDict
from taph.exceptions import ImmutableError
from taph.protocols import Freezable
from taph.tools.freeze_tools import freeze


class MockFreezableToImmutable:
    """A freezable mock returning an atomic immutable type."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __freeze__(self) -> int:
        return self.value


class MockFreezableToMutable:
    """A freezable mock returning a mutable type needing recursive freeze."""

    def __init__(self, value: list[int]) -> None:
        self.value = value

    def __freeze__(self) -> list[int]:
        return self.value


class HashableFreezable:
    """A custom hashable class that implements Freezable.

    Allows testing frozenset/tuple optimization branches where elements
    are structurally non-immutable initially but become immutable.
    """

    def __init__(self, value: int) -> None:
        self.value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashableFreezable):
            return NotImplemented
        return self.value == other.value

    def __freeze__(self) -> int:
        return self.value


class CustomMapping(Mapping[str, list[int]]):
    """A custom Mapping implementing the standard Mapping interface."""

    def __init__(self, data: dict[str, list[int]]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> list[int]:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class CustomSequence(Sequence[list[int]]):
    """A custom Sequence implementing the standard Sequence interface."""

    def __init__(self, data: list[list[int]]) -> None:
        self._data = data

    def __getitem__(self, index: Any) -> Any:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


class UnfreezableType:
    """A completely unfreezable custom type."""

    pass


def test_freeze_atoms() -> None:
    """Verify basic atomic types pass through unchanged."""
    assert freeze(42) == 42
    assert freeze('taph') == 'taph'
    assert freeze(None) is None
    assert freeze(b'bytes') == b'bytes'


def test_freeze_already_frozen() -> None:
    """Verify already immutable Taph containers pass through unchanged (idempotency)."""
    fd = FrozenDict({'a': 1})
    assert freeze(fd) is fd


def test_freeze_freezable_to_immutable() -> None:
    """Verify Freezable returning an already immutable value bypasses recursion."""
    obj = MockFreezableToImmutable(100)
    assert freeze(obj) == 100


def test_freeze_freezable_to_mutable() -> None:
    """Verify Freezable returning a mutable value triggers deep recursive freezing."""
    obj = MockFreezableToMutable([1, 2])
    assert freeze(obj) == (1, 2)


def test_freeze_deque() -> None:
    """Verify deques are recursively frozen into tuples."""
    dq = deque([[1, 2], [3, 4]])
    assert freeze(dq) == ((1, 2), (3, 4))


def test_freeze_dict() -> None:
    """Verify standard dictionaries are recursively frozen into FrozenDicts."""
    d = {'a': [1, 2], 'b': {'c': [3]}}
    frozen = freeze(d)
    assert isinstance(frozen, FrozenDict)
    assert frozen['a'] == (1, 2)
    assert isinstance(frozen['b'], FrozenDict)
    assert frozen['b']['c'] == (3,)


def test_freeze_frozenset_fast_path() -> None:
    """Verify optimized frozenset branch when all items are already immutable."""
    fs = frozenset([1, 2, 3])
    assert freeze(fs) is fs


def test_freeze_frozenset_recursive_path() -> None:
    """Verify frozenset branch when elements must be recursively processed."""
    # Using HashableFreezable to avoid Python's unhashable type checks on sets
    fs = frozenset([HashableFreezable(10)])
    frozen = freeze(fs)
    assert frozen == frozenset([10])


def test_freeze_list() -> None:
    """Verify lists are recursively frozen into tuples."""
    lst = [[1, 2], [3, [4]]]
    assert freeze(lst) == ((1, 2), (3, (4,)))


def test_freeze_set() -> None:
    """Verify standard sets are recursively frozen into frozensets."""
    s = {1, 2, 3}
    frozen = freeze(s)
    assert isinstance(frozen, frozenset)
    assert frozen == frozenset([1, 2, 3])


def test_freeze_tuple_fast_path() -> None:
    """Verify optimized tuple branch when all items are already immutable."""
    tup = (1, 2, 3)
    assert freeze(tup) is tup


def test_freeze_tuple_recursive_path() -> None:
    """Verify tuple branch when elements are mutable and require recursion."""
    tup = (1, [2, 3])
    assert freeze(tup) == (1, (2, 3))


def test_freeze_custom_mapping() -> None:
    """Verify custom (non-dict) mappings are frozen into FrozenDicts."""
    cm = CustomMapping({'key': [1, 2]})
    frozen = freeze(cm)
    assert isinstance(frozen, FrozenDict)
    assert frozen['key'] == (1, 2)


def test_freeze_custom_sequence() -> None:
    """Verify custom sequences are recursively frozen into tuples."""
    cs = CustomSequence([[1, 2]])
    assert freeze(cs) == ((1, 2),)


def test_freeze_unfreezable_type_error() -> None:
    """Verify that passing an unfreezable type raises ImmutableError."""
    with pytest.raises(ImmutableError, match='cannot be frozen'):
        freeze(UnfreezableType())


def test_freeze_cycles() -> None:
    """Verify safety bounds when encountering circular reference structures."""
    cyclic_list: list[Any] = []
    cyclic_list.append(cyclic_list)
    with pytest.raises((RecursionError, ImmutableError)):
        freeze(cyclic_list)
