"""Immutable Record module.

This module provides the `Record` base class and its associated view classes,
designed for creating lightweight, immutable, hashable data containers
similar to `dataclasses` or `namedtuple`, but with:

- `__slots__`-based memory efficiency
- Automatic content-based digest (hash) as the last slot
- Mapping-like interface (keys(), values(), items(), get(), ...)
- Zero-allocation accessors where possible
- Hash stability based on content (not identity)
- Structural subclass registration via __subclasshook__

"""

from __future__ import annotations

import itertools
from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
)
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import NotImplementedType

from taph.config.meta_conf import record_type_conf as error_msg
from taph.config.meta_conf import taph_type_conf as taph
from taph.exceptions import ImmutableError, RecordError
from taph.meta.record_meta import RecordType
from taph.protocols import Immutable
from taph.tools.hash_tools import content_id, hash_id, hex_id
from taph.views.record_views import (
    RecordItemsView,
    RecordKeysView,
    RecordValuesView,
)


class Record(metaclass=RecordType):
    """Base class for creating immutable value objects with content hashing.

    Subclasses must define `__slots__` with field names + final `digest` slot.
    The digest field is managed automatically and should **not** be set
    manually.

    Implements parts of the `Mapping` protocol (read-only) and is hashable
    based on the digest of the content.

    """

    __slots__: tuple[str, ...] = ()
    __digest__: bytes

    def __contains__(self, key: str) -> bool:
        """Check if a string is a field name.

        Args:
            key (str): The field to test for membership

        Returns:
            bool: True if the key is one of the record's fields

        """
        return key != taph.digest and key in self.__class__.__slots__

    def __copy__(self) -> Record:
        """Return self, Record is immutable."""
        return self

    def __deepcopy__(self, memo: dict[int, object]) -> Record:
        """Return self, Record is deeply immutable."""
        return self

    def __dir__(self) -> list[str]:
        """Return list of public attributes and fields."""
        standard = {k for k in super().__dir__() if not k.startswith('_')}
        standard.update(self.__class__.__slots__[:-1])
        return list(standard)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        """Return equality based on __digest__.

        Args:
            other (object): The object to compare equality with.

        Returns:
            bool: True if the both objects have the same content digest.

        """
        if other is self:
            return True

        if isinstance(other, Immutable):
            return self.__digest__ == other.__digest__

        return NotImplemented

    def __getitem__(self, key: str) -> object:
        """Provide field lookup via indexing & slicing.

        Args:
            key (str): Field name to retrieve

        Returns:
            The value of the requested field

        Raises:
            KeyError: If the key is not a valid field or is the digest field

        """
        if key == taph.digest:
            raise KeyError(key)
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError from None

    def __hash__(self) -> int:
        """Return a hash based on the record's content digest.

        The hash is stable and content-based. The same fields and same values
        return the same hash.

        Returns:
            int: An integer hash base on all fields names and values.

        """
        return hash_id(self.__digest__)

    def __iter__(self) -> Iterator[str]:
        """Iterate over field names, excluding the digest field.

        Yields:
            str: Field names in order, excluding the digest field.

        """
        return itertools.islice(
            self.__class__.__slots__, len(self.__class__.__slots__) - 1
        )

    def __len__(self) -> int:
        """Return the number of user-defined fields (excludes digest).

        Returns:
            int: The number of fields in this record.

        """
        return len(self.__class__.__slots__) - 1

    def __ne__(self, other: object) -> bool:
        """Return inequality if both objects are Immutable.

        Args:
            other (object): An Immutable object to compare ineqaulity with.

        Returns:
            bool: True if both objects have different content digests.

        """
        res = self.__eq__(other)
        if res is NotImplemented:
            return NotImplemented
        return not res

    def __replace__(self, /, **changes: object) -> Record:
        """Return a new Record with specified fields replaced.

        Implements copy.replace support for creating modified copies.

        Args:
            **changes: Field names and their new values.

        Returns:
            Record: A new Record instance with updated fields.

        """
        if not changes:
            return self

        fields = cast('tuple[str, ...]', self.__class__.__slots__[:-1])

        kwargs: dict[str, object] = {k: getattr(self, k) for k in fields}
        kwargs.update(changes)

        return self.__class__(**kwargs)

    def __repr__(self) -> str:
        """Return a string representation of the Record.

        Returns:
            str: A string: ClassName(field1=value1, field2=value2, ...).

        """
        args = ', '.join(f'{k}={v!r}' for k, v in self.items())
        return f'{self.__class__.__name__}({args})'

    def get(self, key: str, default: object = None) -> object:
        """Perform a safe field lookup.

        Args:
            key (str): Field name to retrieve.
            default (object, optional): Value returned if key is not found
                or is the digest field. Defaults to None.

        Returns:
            object: Field value or default if not found.

        """
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> RecordKeysView:
        """Return a set-like view of the field names (excludes digest).

        Returns:
            RecordKeysView: A view of the record's field names.

        """
        return RecordKeysView(self)

    def values(self) -> RecordValuesView:
        """Return a view of the field values.

        Returns:
            RecordValuesView: A view of the record's field values.

        """
        return RecordValuesView(self)

    def items(self) -> RecordItemsView:
        """Return a set-like view of (field_name, value) pairs.

        Returns:
            RecordItemsView: A view of the record's (key, value) pairs.

        """
        return RecordItemsView(self)

    def pop(self, item: object) -> None:
        """Raise a TypeError for mutation on an immutable object.

        Args:
            item (object): The field to remove (not used).

        Raises:
            ImmutableError: Always raised; Records are immutable.

        """
        raise ImmutableError(error_msg.pop(item, self.__class__.__name__))

    def popitem(self) -> None:
        """Raise a TypeError for mutation on an immutable object.

        Raises:
            ImmutableError: Always raised; Records are immutable.

        """
        raise ImmutableError(error_msg.record(self.__class__.__name__))

    def update(
        self,
        items: Mapping[object, object] | Iterable[object],  # noqa ARG002
    ) -> None:
        """Raise a TypeError for mutation on an immutable object.

        Args:
            items (Mapping | Iterable): Items to update (not used).

        Raises:
            ImmutableError: Always raised; Records are immutable.

        """
        raise ImmutableError(error_msg.record(self.__class__.__name__))

    def setdefault(self, key: str, default: object = None) -> None:  # noqa ARG003
        """Raise a TypeError for mutation on an immutable object.

        Args:
            key (str): The field name (not used).
            default (object, optional): The default value (not used).

        Raises:
            ImmutableError: Always raised; Records are immutable.

        """
        raise ImmutableError(error_msg.record(self.__class__.__name__))

    @property
    def fingerprint(self) -> str:
        """Return a url-safe base64-encoded content hash of this record.

        Returns:
            str: A base64-encoded content hash.

        """
        return content_id(self.__digest__)

    @property
    def hexdigest(self) -> str:
        """Return a hexadecimal string of the content hash of this record.

        Returns:
            str: A hexadecimal string representation of the content hash.

        """
        return hex_id(self.__digest__)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Record:
        """Create a Record from a mapping, using known fields.

        Args:
            data (Mapping[str, object]): A mapping of field names to values.

        Returns:
            Record: A new Record instance initialized with values from data.

        Note:
            Only fields defined in __slots__ are used; other keys are ignored.

        """
        expected_fields: set[str] = set(cls.__slots__[:-1])
        provided_fields: set[str] = set(data.keys())
        missing = expected_fields - provided_fields

        if missing:
            raise RecordError(error_msg.missing_fields(cls.__name__, missing))

        known = {k: data[k] for k in expected_fields}
        return cls(**known)

    @classmethod
    def fromkeys(cls, keys: Iterable[str], value: object = None) -> None:
        """Create a new Record from a sequence of keys (not implemented).

        This method exists for Mapping compatibility but is not supported
        for Record objects.

        Args:
            keys (Iterable[str]): A sequence of field names (not used).
            value (object, optional): A default value (not used).

        Raises:
            NotImplementedError: Always returns NotImplemented.

        """
        raise NotImplementedError(error_msg.not_implemented)

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool | NotImplementedType:
        """Register structural virtual subclasses.

        A class is recognized as a Record if its __slots__ ends with
        the digest field name.

        Args:
            subclass (type): The class to check for Record compatibility.

        Returns:
            bool: True if subclass is a Record,

        """
        if cls is Record:
            for base in subclass.__mro__:
                slots = getattr(base, '__slots__', ())
                if slots and slots[-1] == taph.digest:
                    return True
        return NotImplemented  # type: ignore[no-any-return]


Mapping.register(Record)
