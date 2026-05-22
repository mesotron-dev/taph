"""Views module for the taph.record.Record."""

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

    from taph.record import Record
from taph.tools.hash_tools import hash_id, mk_digest

__all__: tuple[str, ...] = (
    'RecordItemsView',
    'RecordKeysView',
    'RecordValuesView',
)
_T = TypeVar('_T')


class RecordKeysView(KeysView[str]):
    """A set-like view of a Record's keys.

    Provides a read-only set-like interface to access a Record's field names,
    excluding the digest field.

    """

    __slots__ = ()

    def __init__(self, record: Record) -> None:
        """Initialize the view with a Record instance.

        Args:
            record (Record): The Record to create a view for.

        """
        self._mapping = record

    def __len__(self) -> int:
        """Return the number of Record fields.

        Returns:
            int: The number of fields (excluding digest).

        """
        return len(self._mapping.__class__.__slots__) - 1

    def __iter__(self) -> Iterator[str]:
        """Iterate over field names (excluding digest).

        Yields:
            str: Field names in order.

        """
        return iter(self._mapping.__class__.__slots__[:-1])

    def __contains__(self, item: object) -> bool:
        """Check if a field exists in the Record.

        Args:
            item (object): The field name to check.

        Returns:
            bool: True if the field exists.

        """
        if not isinstance(item, str):
            return False

        return item in self._mapping

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Check equality with another set-like view.

        Args:
            other (object): Another set-like object to compare with.

        Returns:
            bool | NotImplementedType:
                True if equal, NotImplemented if types are incompatible.

        """
        if not isinstance(other, (AbstractSet, RecordKeysView)):
            return NotImplemented
        return len(self) == len(other) and all(item in other for item in self)

    def __le__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a subset of another set.

        Args:
            other (AbstractSet[object]): Another set to compare with.

        Returns:
            bool: True if this view is a subset of the other.

        """
        return len(self) <= len(other) and all(item in other for item in self)

    def __lt__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a proper subset of another set.

        Args:
            other (AbstractSet[object]): Another set to compare with.

        Returns:
            bool: True if this view is a proper subset of the other.

        """
        return len(self) < len(other) and all(item in other for item in self)

    def __ge__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a superset of another set.

        Args:
            other (AbstractSet[object]): Another set to compare with.

        Returns:
            bool: True if this view is a superset of the other.

        """
        return len(self) >= len(other) and all(item in self for item in other)

    def __gt__(self, other: AbstractSet[object]) -> bool:
        """Check if this is a proper superset of another set.

        Args:
            other (AbstractSet[object]): Another set to compare with.

        Returns:
            bool: True if this view is a proper superset of the other.

        """
        return len(self) > len(other) and all(item in self for item in other)

    def __and__(self, other: Iterable[object]) -> set[str]:
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

    def __or__(self, other: Iterable[_T]) -> set[str | _T]:
        """Return the union of this view with another iterable.

        Args:
            other: An iterable to union with this view

        Returns:
            A set containing all elements from this view and other

        """
        return set(self) | set(other)

    def __ror__(self, other: Iterable[_T]) -> set[str | _T]:
        """Return the union of another iterable with this view.

        Called when the left operand doesn't support __or__.

        Args:
            other: An iterable to union with this view

        Returns:
            A set containing all elements from other and this view

        """
        return set(other) | set(self)

    def __sub__(self, other: Iterable[object]) -> set[str]:
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

    def __xor__(self, other: Iterable[_T]) -> set[str | _T]:
        """Return the symmetric difference of this view and another iterable.

        Args:
            other: An iterable to compute symmetric difference with

        Returns:
            A set containing elements in either this view or anoother,
            but not both

        """
        return set(self) ^ set(other)

    def __rxor__(self, other: Iterable[_T]) -> set[str | _T]:
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

        The hash is based on the record's field names (excludes digest).

        Returns:
            An integer hash value based on the view's contents

        """
        return hash_id(mk_digest(self._mapping.__class__.__slots__[:-1]))


class RecordItemsView(ItemsView[str, object]):
    """A set-like view of a Record's items."""

    __slots__ = ()

    def __init__(self, record: Record) -> None:
        """Initialize the view with a Record instance.

        Args:
            record (Record): The Record to create a view for.

        """
        self._mapping = record

    def __len__(self) -> int:
        """Return the number of (key, value) pairs.

        Returns:
            int: The number of (key, value) pairs in this record.

        """
        return len(self._mapping)

    def __iter__(self) -> Iterator[tuple[str, object]]:
        """Iterate over (key, value) pairs.

        Yields:
            str: (key, value) in order.

        """
        slots: tuple[str, ...] = self._mapping.__class__.__slots__[:-1]
        yield from ((key, getattr(self._mapping, key)) for key in slots)

    def __contains__(self, item: object) -> bool:
        """Check if a (key, value) pair exists.

        Args:
            item (str): The item to test for membership

        Returns:
            bool: True if the (key, value) pair exists

        """
        if not isinstance(item, tuple) or len(item) != 2:
            return False

        key, value = item
        if not isinstance(key, str):
            return False

        if key in self._mapping:
            return bool(getattr(self._mapping, key) == value)

        return False

    def __eq__(self, other: object) -> bool:
        """Check equality with another items view."""
        if not isinstance(other, (ItemsView, RecordItemsView)):
            return NotImplemented
        return len(self) == len(other) and all(item in other for item in self)

    def __hash__(self) -> int:
        """Return hash of the items."""
        return hash_id(self._mapping.__digest__)


class RecordValuesView(ValuesView[object]):
    """A set-like view of a Record's values."""

    __slots__ = ()

    def __init__(self, record: Record) -> None:
        self._mapping = record

    def __len__(self) -> int:
        """Return the number of values."""
        return len(self._mapping)

    def __iter__(self) -> Iterator[object]:
        """Iterate over values."""
        slots: tuple[str, ...] = self._mapping.__class__.__slots__[:-1]
        yield from (getattr(self._mapping, key) for key in slots)

    def __contains__(self, value: object) -> bool:
        """Check if a value exists in the Record."""
        slots: tuple[str, ...] = self._mapping.__class__.__slots__[:-1]
        return any(getattr(self._mapping, str(key)) == value for key in slots)

    def __eq__(self, other: object) -> bool:
        """Check equality with another values view."""
        if not isinstance(other, (ValuesView, RecordValuesView)):
            return NotImplemented
        return len(self) == len(other) and all(value in other for value in self)

    def __hash__(self) -> int:
        """Return hash of the values."""
        slots: tuple[str, ...] = self._mapping.__class__.__slots__[:-1]
        values = tuple(getattr(self._mapping, slot) for slot in slots)
        return hash_id(mk_digest(values))
