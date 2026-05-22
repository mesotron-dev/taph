"""Views module for the taph.manifest.Manifest."""

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
    from taph.manifest import Manifest
from taph.config.meta_conf import manifest_type_conf as manifest
from taph.tools.hash_tools import hash_id, mk_digest

__all__: tuple[str, ...] = (
    'ManifestItemsView',
    'ManifestKeysView',
    'ManifestValuesView',
)
_Manifest = TypeVar('_Manifest', bound='Manifest[str, object]')
_T = TypeVar('_T')


class ManifestKeysView(KeysView[str]):
    """A set-like view of a Manifest's keys.

    Provides a read-only set-like interface to access a Manifest's field names,
    excluding the digest field.

    """

    __slots__ = ()

    def __init__(self, manifest: type[_Manifest]) -> None:
        """Initialize the view with a Manifest instance.

        Args:
            manifest (Manifest): The Manifest to create a view for.

        """
        self._mapping: type[_Manifest] = manifest

    def __contains__(self, field: object) -> bool:
        """Check if a field exists in the Manifest.

        Args:
            field (str): The field name to check.

        Returns:
            bool: True if the field exists.

        """
        if not isinstance(field, str):
            return False
        return field in getattr(self._mapping, manifest.keys, ())

    def __len__(self) -> int:
        """Return the number of Manifest fields.

        Returns:
            int: The number of fields (excluding digest).

        """
        return len(getattr(self._mapping, manifest.keys, ()))

    def __iter__(self) -> Iterator[str]:
        """Iterate over field names (excluding digest).

        Yields:
            str: Field names in order.

        """
        return iter(getattr(self._mapping, manifest.keys, ()))

    def __eq__(self, other: object) -> bool:
        """Check keys equality with another set-like view.

        Args:
            other (object): Another set-like object to compare with.

        Returns:
            bool | NotImplementedType:
                True if equal, NotImplemented if types are incompatible.

        """
        if isinstance(other, (AbstractSet, ManifestKeysView)):
            if len(self) != len(other):
                return False
            keys = set(getattr(self._mapping, manifest.keys, {}))
            return all(key in other for key in keys)

        return NotImplemented

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
            A _Tset containing elements present in both other and this view

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

        The hash is based on the manifest's field names (excludes digest).

        Returns:
            An integer hash value based on the view's contents

        """
        keys: tuple[str, ...] = getattr(self._mapping, manifest.keys, ())
        return hash_id(mk_digest(keys))


class ManifestItemsView(ItemsView[str, object]):
    """A set-like view of a Manifest's items."""

    __slots__ = ()

    def __init__(self, manifest: type[_Manifest]) -> None:
        """Initialize the view with a Manifest instance.

        Args:
            manifest (Manifest): The Manifest to create a view for.

        """
        self._mapping = manifest

    def __len__(self) -> int:
        """Return the number of (key, value) pairs.

        Returns:
            int: The number of (key, value) pairs in this manifest.

        """
        return len(self._mapping)

    def __iter__(self) -> Iterator[tuple[str, object]]:
        """Iterate over (key, value) pairs.

        Yields:
            str: (key, value) in order.

        """
        keys: tuple[str, ...] = getattr(self._mapping, manifest.keys, ())
        values: tuple[object, ...] = getattr(
            self._mapping, manifest.values, ())
        yield from zip(keys, values, strict=True)

    def __contains__(self, item: object) -> bool:
        """Check if a (key, value) pair exists.

        Args:
            item (tuple[str, object]): The item to test for membership

        Returns:
            bool: True if the (key, value) pair exists

        """
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        key, value = item
        return key in self._mapping and getattr(self._mapping, key) == value

    def __eq__(self, other: object) -> bool:
        """Check equality with another items view."""
        if not isinstance(other, (AbstractSet, ItemsView, ManifestKeysView)):
            return NotImplemented
        return len(self) == len(other) and all(
            item in other for item in self
        )

    def __hash__(self) -> int:
        """Return hash of the items."""
        return hash_id(self._mapping.__digest__)


class ManifestValuesView(ValuesView[object]):
    """A set-like view of a Manifest's values."""

    __slots__ = ()

    def __init__(self, manifest: type[_Manifest]) -> None:
        self._mapping = manifest

    def __len__(self) -> int:
        """Return the number of values."""
        values: tuple[str, ...] = getattr(self._mapping, manifest.values, ())
        return len(values)

    def __iter__(self) -> Iterator[object]:
        """Iterate over values."""
        yield from (
            value for value in getattr(self._mapping, manifest.values, ())
        )

    def __contains__(self, value: object) -> bool:
        """Check if a value exists in the Manifest."""
        values: tuple[str, ...] = getattr(self._mapping, manifest.values, ())
        return value in values

    def __eq__(self, other: object) -> bool:
        """Check equality with another values view."""
        if not isinstance(other, (ValuesView, ManifestValuesView)):
            return NotImplemented
        return len(self) == len(other) and all(value in other for value in self)

    def __hash__(self) -> int:
        """Return hash of the values."""
        return hash_id(mk_digest(getattr(self._mapping, manifest.values, ())))
