"""The hashable immutable dictionary module.

#TODO

"""

import bisect
import sys
from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
)
from typing import Self, TypeVar, overload

from taph.config.meta_conf import frozen_dict_conf as error_msg
from taph.config.meta_conf import taph_type_conf as taph
from taph.exceptions import ImmutableError
from taph.meta.frozen_dict_meta import FrozenDictType
from taph.tools.hash_tools import content_id, hash_id, hex_id, mk_digest
from taph.views.frozen_dict_views import (
    FrozenDictItemsView,
    FrozenDictKeysView,
    FrozenDictValuesView,
)

__all__ = ('FrozenDict',)
_T = TypeVar('_T')


class FrozenDict[Key, Value](Mapping[Key, Value], metaclass=FrozenDictType):
    """A hashable, immutable dictionary.

    #TODO
    """

    __slots__: tuple[str, ...] = ('__digest__', '_index_', '_keys_', '_values_')

    _index_: tuple[tuple[bytes, int], ...]
    _keys_: tuple[Key, ...]
    _values_: tuple[Value, ...]
    __digest__: bytes

    def __freeze__(self) -> Self:
        """Identity mapping for the Freezable protocol."""
        return self

    def __thaw__(self) -> dict[Key, Value]:
        """Implement the Thawable protocol.

        Returns:
            A mutable dictionary representation.

        """
        return dict(zip(self._keys_, self._values_, strict=True))

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize a deeply frozen dictionary.

        Note: This is bypassed at runtime by FrozenDictType.__call__
        to enforce immutability on creation. It exists for type hinting.
        """

    def __contains__(self, key: object) -> bool:
        """Check for the existence of a given key.

        Args:
            key (object): The key object to test for membership.

        Returns:
            bool: True if the key is a member of the FrozenDict's.

        """
        if key == taph.digest:
            raise KeyError(key)

        key_digest = mk_digest(key)
        position = bisect.bisect_left(
            self._index_, key_digest, key=lambda x: x[0]
        )
        if position < len(self._index_):
            stored_digest, index = self._index_[position]
            if stored_digest == key_digest and self._keys_[index] == key:
                return self._values_[index]  # type: ignore

        return False

    def __copy__(self) -> Self:
        """Return self, FrozenDict is immutable.

        Returns:
            FrozenDict: Return this frozen dictionary.

        """
        return self

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        """Return self, FrozenDict is immutable.

        Since FrozenDict elements are frozen at creation, the structure
        is safely shared across deep copies without duplication.

        Args:
            memo: Memo is not used
        Returns:
            FrozenDict: Return this frozen dictionary.

        """
        return self



    def __dir__(self) -> list[str]:
        """Return list of public attributes and fields."""
        # pragma: no cover
        return [
            attr
            for attr in super().__dir__()
            if attr not in ('_index_', '_keys_', '_values_')
        ]

    def __eq__(self, other: object) -> bool:
        """Compare the digest of this FrozenDict to another.

        Returns:
            bool: True if this frozen dictionary keys & value's match another

        """
        if hasattr(other, taph.digest):
            return bool(self.__digest__ == getattr(other, taph.digest))
        return NotImplemented

    def __getitem__(self, key: Key) -> Value:
        """Provide a value for a given key.

        Args:
            key (str): Field name to retrieve

        Returns:
            The value of the requested field

        Raises:
            KeyError: If the key is not a valid field or is the digest field

        """
        if key == taph.digest:
            raise KeyError(key)

        key_digest = mk_digest(key)
        position = bisect.bisect_left(
            self._index_, key_digest, key=lambda x: x[0]
        )
        if position < len(self._index_):
            stored_digest, index = self._index_[position]
            if stored_digest == key_digest and self._keys_[index] == key:
                return self._values_[index]

        raise KeyError(key)

    def __hash__(self) -> int:
        """Return a hash based on the FrozenDict's content digest.

        The hash is stable and content-based. The same keys and values
        return the same hash.

        Returns:
            An integer hash base on all keys and values.

        """
        return hash_id(self.__digest__)

    def __iter__(self) -> Iterator[Key]:
        """Iterate over the keys of the dictionary.

        Yields:
            object: The key objects of the dictionary.

        """
        yield from self._keys_

    def __len__(self) -> int:
        """Return the number of items in the dictionary.

        Returns:
            int: The number of items in the dictionary.

        """
        return len(self._keys_)

    def __ne__(self, other: object) -> bool:
        """Return self != other."""
        if hasattr(other, taph.digest):
            return bool(self.__digest__ != getattr(other, taph.digest))
        return NotImplemented

    def __or__(self, other: object) -> FrozenDict[Key, Value]:
        if isinstance(other, Mapping):
            data = dict(zip(self._keys_, self._values_, strict=True))
            data.update(other)
            return FrozenDict(data)
        return NotImplemented

    def __ror__(self, other: object) -> FrozenDict[Key, Value]:
        if isinstance(other, Mapping):
            data = dict(other)
            data.update(zip(self._keys_, self._values_, strict=True))
            return FrozenDict(data)
        return NotImplemented

    def __init_subclass__(cls) -> None:
        """Prevent subclassing of immutable mappings.

        Raises:
            TypeError: Always raised on attempt to subclass.

        """
        raise TypeError(error_msg.subclass(cls.__name__))

    def __repr__(self) -> str:
        """Return a string representation of the FrozenDict.

        Returns:
            str: A string for all keys and values of the dictionary.

        """
        body = ', '.join(
            f'{k!r}: {v!r}'
            for k, v in zip(self._keys_, self._values_, strict=True)
        )
        return f'FrozenDict({{{body}}})'

    def __sizeof__(self) -> int:
        """Return the size of the FrozenDict in bytes.

        Returns:
            int: The size of FrozenDict in bytes.

        """
        size = super().__sizeof__()
        size += sys.getsizeof(self._index_)
        size += sys.getsizeof(self._keys_)
        size += sys.getsizeof(self._values_)
        size += sys.getsizeof(self.__digest__)
        return size

    @overload
    def get(self, key: Key, /) -> Value: ...

    @overload
    def get(self, key: Key, /, default: Value) -> Value: ...

    @overload
    def get(self, key: Key, /, default: _T) -> Value | _T: ...

    def get(self, key: Key, default: object = None) -> object:
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

    def keys(self) -> FrozenDictKeysView[Key, Value]:
        """Return a set-like view of the keys of this Mapping.

        Returns:
            FrozenDictKeysView: A view of the record's field names.

        """
        """Return a view of the keys in a ."""
        return FrozenDictKeysView(self)

    def values(self) -> FrozenDictValuesView[Key, Value]:
        """Return a view of the values in a FrozenDict."""
        return FrozenDictValuesView(self)

    def items(self) -> FrozenDictItemsView[Key, Value]:
        """Return a view of the items in a FrozenDict."""
        return FrozenDictItemsView(self)

    def pop(self, *args: object, **kwargs: object) -> None:  # noqa ARG003
        """Cannot modify a FrozenDict."""
        raise ImmutableError(error_msg.immutable(self.__class__.__name__))

    def popitem(self) -> None:
        """Cannot modify a FrozenDict."""
        raise ImmutableError(error_msg.immutable(self.__class__.__name__))

    def clear(self) -> None:
        """Cannot modify a FrozenDict."""
        raise ImmutableError(error_msg.immutable(self.__class__.__name__))

    def copy(self) -> FrozenDict[Key, Value]:
        """Return the immutable self."""
        return self

    def update(self, *args: object, **kwargs: object) -> None:  # noqa ARG003
        """Raise a TypeError for mutation on an immutable object.

        Raises:
            TypeError: Always raised; Records are immutable.

        """
        raise TypeError(error_msg.immutable(self.__class__.__name__))

    def setdefault(self, key: str, default: object = None) -> None:  # noqa ARG003
        """Raise a TypeError for mutation on an immutable object.

        Args:
            key (str): The field name (not used).
            default (object, optional): The default value (not used).

        Raises:
            TypeError: Always raised; Records are immutable.

        """
        raise TypeError(error_msg.immutable(self.__class__.__name__))

    @property
    def fingerprint(self) -> str:
        """Return a url-safe base64-encoded content hash of this FrozenDict.

        Returns:
            str: A base64-encoded content hash.

        """
        return content_id(self.__digest__)

    @property
    def hexdigest(self) -> str:
        """Return a hexadecimal string of the content hash of this FrozenDict.

        Returns:
            str: A hexadecimal string representation of the content hash.

        """
        return hex_id(self.__digest__)

    @classmethod
    def fromkeys(cls, keys: Iterable[str], value: object = None) -> None:
        """Create a new FrozenDict from a sequence of keys (not implemented).

        This method exists for Mapping compatibility but is not supported.

        Args:
            keys (Iterable[str]): A sequence of field names (not used).
            value (object, optional): A default value (not used).

        Raises:
            NotImplementedError: fromkeys is not implemented for FrozenDict

        """
        raise NotImplementedError(error_msg.not_implemented)


Mapping.register(FrozenDict)
