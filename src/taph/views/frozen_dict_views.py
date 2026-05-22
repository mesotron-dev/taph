"""Views module for the taph.frozen_dict.FrozenDict."""

import bisect
from collections.abc import (
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    ValuesView,
)
from collections.abc import Set as AbstractSet
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from types import NotImplementedType

    from taph.frozen_dict import FrozenDict


from taph.tools.hash_tools import hash_id, mk_digest

__all__: tuple[str, ...] = (
    'FrozenDictItemsView',
    'FrozenDictKeysView',
    'FrozenDictValuesView',
)
_T = TypeVar('_T')


class FrozenDictKeysView[Key, Value](KeysView[Key]):
    """A set-like view of a FrozenDict's keys.

    Provides a read-only set-like interface to access a FrozenDict's field
    names, excluding the digest field.

    """

    __slots__ = ()

    def __init__(self, frozendict: FrozenDict[Key, Value]) -> None:
        """Initialize the view with a FrozenDict instance.

        Args:
            frozendict (FrozenDict): The frozendict to create a view for.

        """
        self._mapping = frozendict

    def __len__(self) -> int:
        """Return the number of FrozenDict fields.

        Returns:
            int: The number of fields (excluding digest).

        """
        return len(self._mapping._keys_)

    def __iter__(self) -> Iterator[Key]:
        """Iterate over field names (excluding digest).

        Yields:
            str: Field names in order.

        """
        return iter(self._mapping._keys_)

    def __contains__(self, key: object) -> bool:
        """Check if a key exists in the FrozenDict.

        Args:
            key (object): The field name to check.

        Returns:
            bool: True if the field exists.

        """
        key_hash = mk_digest(key)
        position = bisect.bisect_left(
            self._mapping._index_, key_hash, key=lambda x: x[0]
        )
        if position < len(self._mapping._index_):
            stored_hash, index = self._mapping._index_[position]
            if (
                stored_hash == key_hash
                and self._mapping._keys_[index] == key
            ):
                return True
        return False

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Check equality with another set-like view.

        Args:
            other (object): Another set-like object to compare with.

        Returns:
            bool | NotImplementedType:
                True if equal, NotImplemented if types are incompatible.

        """
        if not isinstance(other, (AbstractSet, FrozenDictKeysView)):
            return NotImplemented
        return len(self) == len(other) and all(item in other for item in self)

    def __le__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a subset of another set.

        Args:
            other (Set[object]): Another set to compare with.

        Returns:
            bool: True if this view is a subset of the other.

        """
        return len(self) <= len(other) and all(item in other for item in self)

    def __lt__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a proper subset of another set.

        Args:
            other (Set[object]): Another set to compare with.

        Returns:
            bool: True if this view is a proper subset of the other.

        """
        return len(self) < len(other) and all(item in other for item in self)

    def __ge__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a superset of another set.

        Args:
            other (Set[object]): Another set to compare with.

        Returns:
            bool: True if this view is a superset of the other.

        """
        return len(self) >= len(other) and all(item in self for item in other)

    def __gt__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a proper superset of another set.

        Args:
            other (Set[object]): Another set to compare with.

        Returns:
            bool: True if this view is a proper superset of the other.

        """
        return len(self) > len(other) and all(item in self for item in other)

    def __and__(self, other: Iterable[object]) -> set[Key]:
        """Return the intersection of this view with another iterable.

        Args:
            other: An iterable to intersect with this view

        Returns:
            A set containing elements present in both this view and the other

        """
        return {item for item in self if item in other}

    def __rand__(self, other: Iterable[_T]) -> set[_T]:
        """Return the intersection of another iterable with this view.

        Called when the left operand doesn't support __and__.

        Args:
            other: An iterable to intersect with this view

        Returns:
            A set containing elements present in both other and this view

        """
        return {item for item in other if item in self}

    def __or__(self, other: Iterable[_T]) -> set[Key | _T]:
        """Return the union of this view with another iterable.

        Args:
            other: An iterable to union with this view

        Returns:
            A set containing all elements from this view and other

        """
        return set(self) | set(other)

    def __ror__(self, other: Iterable[_T]) -> set[Key | _T]:
        """Return the union of another iterable with this view.

        Called when the left operand doesn't support __or__.

        Args:
            other: An iterable to union with this view

        Returns:
            A set containing all elements from other and this view

        """
        return set(other) | set(self)

    def __sub__(self, other: Iterable[object]) -> set[Key]:
        """Return the difference of this view minus another iterable.

        Args:
            other: An iterable to subtract from this view

        Returns:
            A set containing elements in this view but not in other

        """
        return {item for item in self if item not in other}

    def __rsub__(self, other: Iterable[_T]) -> set[_T]:
        """Return the difference of another iterable minus this view.

        Called when the left operand doesn't support __sub__.

        Args:
            other: An iterable from which to subtract this view

        Returns:
            A set containing elements in other but not in this view

        """
        return {item for item in other if item not in self}

    def __xor__(self, other: Iterable[_T]) -> set[Key | _T]:
        """Return the symmetric difference of this view and another iterable.

        Args:
            other: An iterable to compute symmetric difference with

        Returns:
            A set containing elements in either this view or anoother,
            but not both

        """
        return set(self) ^ set(other)

    def __rxor__(self, other: Iterable[_T]) -> set[Key | _T]:
        """Return the symmetric difference of another iterable and this view.

        Called when the left operand doesn't support __xor__.

        Args:
            other: An iterable to compute symmetric difference with

        Returns:
            A set containing elements in either other or this view,
            but not both

        """
        return set(other) ^ set(self)

    def isdisjoint(self, other: Iterable[object]) -> bool:
        """Check if this view has no elements in common with another iterable.

        Args:
            other: An iterable to check for common elements

        Returns:
            True if this view and other have no elements in common,
            False otherwise

        """
        return all(item not in other for item in self)

    def __hash__(self) -> int:
        """Return a hash of the view's keys.

        The hash is based on the frozendict's field names (excludes digest).

        Returns:
            An integer hash value based on the view's contents

        """
        return hash_id(mk_digest(self._mapping._keys_))


class FrozenDictItemsView[Key, Value](ItemsView[Key, Value]):
    """A set-like view of a FrozenDict's items."""

    __slots__ = ()

    def __init__(self, frozendict: FrozenDict[Key, Value]) -> None:
        """Initialize the view with a FrozenDict instance.

        Args:
            frozendict (FrozenDict): The frozendict to create a view for.

        """
        self._mapping = frozendict

    def __len__(self) -> int:
        """Return the number of (key, value) pairs.

        Returns:
            int: The number of (key, value) pairs in this frozendict.

        """
        return len(self._mapping._keys_)

    def __iter__(self) -> Iterator[tuple[Key, Value]]:
        """Iterate over (key, value) pairs.

        Yields:
            object: (key, value) iterator.

        """
        yield from zip(
            self._mapping._keys_, self._mapping._values_, strict=True
        )

    def __contains__(self, item: object) -> bool:
        """Check if a key pair exists.

        Args:
            item (tuple[object, object]): The field to test for membership

        Returns:
            bool: True if the key exists.

        """
        if not isinstance(item, tuple) or len(item) != 2:
            return False

        key, value = item
        if key in self._mapping:
            return bool(self._mapping[key] == value)
        return False

    def __eq__(self, other: object) -> bool:
        """Check equality with another items view."""
        if not isinstance(other, (ItemsView, FrozenDictItemsView)):
            return NotImplemented
        return len(self) == len(other) and all(item in other for item in self)

    def __hash__(self) -> int:
        """Return hash of the items."""
        return hash_id(self._mapping.__digest__)


class FrozenDictValuesView[Key, Value](ValuesView[Value]):
    """A set-like view of a FrozenDict's values."""

    __slots__ = ()

    def __init__(self, frozendict: FrozenDict[Key, Value]) -> None:
        self._mapping = frozendict

    def __len__(self) -> int:
        """Return the number of values."""
        return len(self._mapping._values_)

    def __iter__(self) -> Iterator[Value]:
        """Iterate over values."""
        return iter(self._mapping._values_)

    def __contains__(self, value: object) -> bool:
        """Check if a value exists in the FrozenDict."""
        return self._mapping._values_.__contains__(value)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Check equality with another values view."""
        if not isinstance(other, (ValuesView, FrozenDictValuesView)):
            return NotImplemented
        return len(self) == len(other) and all(value in other for value in self)

    def __hash__(self) -> int:
        """Return hash of the values."""
        return hash_id(mk_digest(self._mapping._values_))
