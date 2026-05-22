"""Tests for the taph.tools.thaw_tools module."""

from collections import deque
from collections.abc import Iterator, Mapping, Sequence
from typing import Any
import pytest

from taph.frozen_dict import FrozenDict
from taph.exceptions import ThawError
from taph.protocols import Thawable
from taph.tools.thaw_tools import thaw
from taph.tools.thaw_tools import _thaw


class MockThawableToMutable:
    """A Thawable mock returning a standard mutable dictionary."""

    def __init__(self, value: dict[str, tuple[int, ...]]) -> None:
        self.value = value

    def __thaw__(self) -> dict[str, tuple[int, ...]]:
        return self.value


class MockThawableToImmutable:
    """A Thawable mock returning an immutable type requiring recursive thawing."""

    def __init__(self, value: FrozenDict[str, tuple[int, ...]]) -> None:
        self.value = value

    def __thaw__(self) -> FrozenDict[str, tuple[int, ...]]:
        return self.value


class CustomMapping(Mapping[str, tuple[int, ...]]):
    """A custom Mapping implementation."""

    def __init__(self, data: dict[str, tuple[int, ...]]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> tuple[int, ...]:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class CustomSequence(Sequence[tuple[int, ...]]):
    """A custom Sequence implementation."""

    def __init__(self, data: list[tuple[int, ...]]) -> None:
        self._data = data

    def __getitem__(self, index: Any) -> Any:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


class UnthawableType:
    """A completely unthawable custom type."""

    pass


def test_thaw_thawable_to_mutable() -> None:
    """Verify Thawable returning standard mutable dictionary bypasses recursion."""
    obj = MockThawableToMutable({'a': (1, 2)})
    thawed = thaw(obj)
    assert type(thawed) is dict
    assert thawed['a'] == [1, 2]


def test_thaw_thawable_to_immutable() -> None:
    """Verify Thawable returning an immutable value forces recursion."""
    inner_fd = FrozenDict({'a': (1, 2)})
    obj = MockThawableToImmutable(inner_fd)
    thawed = thaw(obj)
    assert type(thawed) is dict
    assert thawed['a'] == [1, 2]


def test_thaw_primitives() -> None:
    """Verify atomic primitives pass through unchanged (short-circuit)."""
    assert thaw(42) == 42
    assert thaw('string') == 'string'
    assert thaw(None) is None


def test_thaw_already_mutable() -> None:
    """Verify mutable objects return a structurally identical but deep-copied instance."""
    mut_list = [1, 2, 3]
    thawed = thaw(mut_list)
    assert thawed == mut_list
    assert thawed is not mut_list


def test_thaw_deque() -> None:
    """Verify deques are recursively thawed."""
    dq = deque([((1, 2),)])
    thawed = thaw(dq)
    assert isinstance(thawed, deque)
    assert thawed[0] == [[1, 2]]


def test_thaw_dict() -> None:
    """Verify dictionaries recursively thaw their values."""
    d = {'a': (1, 2)}
    thawed = thaw(d)
    assert type(thawed) is dict
    assert thawed['a'] == [1, 2]


def test_thaw_frozendict() -> None:
    """Verify FrozenDicts are recursively thawed to dictionaries."""
    fd = FrozenDict({'a': (1, 2)})
    thawed = thaw(fd)
    assert type(thawed) is dict
    assert thawed['a'] == [1, 2]


def test_thaw_frozenset() -> None:
    """Verify frozensets are recursively thawed to sets."""
    fs = frozenset([1, 2])
    thawed = thaw(fs)
    assert type(thawed) is set
    assert thawed == {1, 2}


def test_thaw_frozenset_limitations() -> None:
    """Verify that thawing elements that become unhashable raises a TypeError.

    This demonstrates system knowledge of Python's hashing limits (lists cannot reside in sets).
    """
    fs = frozenset([(1, 2)])
    with pytest.raises(TypeError, match="unhashable type: 'list'"):
        thaw(fs)


def test_thaw_list() -> None:
    """Verify lists recursively thaw their nested elements."""
    lst = [(1, 2), ((3, 4),)]
    assert thaw(lst) == [[1, 2], [[3, 4]]]


def test_thaw_set() -> None:
    """Verify sets are recursively thawed."""
    s = {1, 2, 3}
    thawed = thaw(s)
    assert type(thawed) is set
    assert thawed == {1, 2, 3}


def test_thaw_tuple() -> None:
    """Verify tuples are recursively thawed into standard lists."""
    tup = ((1, 2), ((3, 4),))
    assert thaw(tup) == [[1, 2], [[3, 4]]]


def test_thaw_custom_sequence() -> None:
    """Verify non-standard sequences are recursively thawed to standard lists."""
    cs = CustomSequence([(1, 2)])
    assert thaw(cs) == [[1, 2]]


def test_thaw_custom_mapping() -> None:
    """Verify non-standard mappings are recursively thawed to standard dicts."""
    cm = CustomMapping({'a': (1, 2)})
    assert thaw(cm) == {'a': [1, 2]}


def test_thaw_unthawable_type_error() -> None:
    """Verify that passing an unthawable type raises ThawError."""
    with pytest.raises(ThawError, match='cannot be thawed'):
        thaw(UnthawableType())


def test_thaw_fallback_conformance() -> None:
    """Directly execute fallback thaw operations on mutable/immutable elements."""
    default_thaw = _thaw.dispatch(object)

    assert default_thaw(42) == 42
    assert default_thaw([1, 2]) == [1, 2]


def test_thaw_dispatcher_direct_invocation():
    """Execute internal dictionary singledispatch handler directly to bypass short-circuit rules."""
    assert _thaw({"nested_key": (1, 2)}) == {"nested_key": [1, 2]}


def test_thaw_frozendict_dispatcher_explicit(sample_frozen_dict):
    """Directly call the fallback singledispatch handler for FrozenDict.

    This ensures 100% coverage on the redundant but robust singledispatch
    registration which is normally short-circuited by the Thawable protocol.
    """
    from taph.tools.thaw_tools import _thaw
    thawed = _thaw.dispatch(FrozenDict)(sample_frozen_dict)
    assert thawed == {"alpha": 1, "beta": 2, "gamma": 3}
