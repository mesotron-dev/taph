"""Utility module for restoring deeply immutable objects to mutable objects.

This module provides the `thaw()` function, which recursively converts immutable
data structures (such as tuples, frozensets, FrozenDict, etc.) into their
mutable counterparts (lists, sets, dicts, etc.), while leaving already mutable
objects unchanged.

The conversion is deep — nested immutable objects are thawed as well.
"""

from collections import deque
from collections.abc import Mapping, Sequence
from functools import singledispatch

from taph.config.tools_conf import thaw_error_messages as error_msg
from taph.exceptions import ThawError
from taph.protocols import Thawable
from taph.tools.core_tools import is_atom, is_immutable, is_mutable

__all__: tuple[str] = ('thaw',)


def thaw(item: object) -> object:
    """Convert an immutable object into a new mutable object.

    This is the default implementation for unregistered types. It checks whether
    the object implements the Thawable protocol, is immutable, or is already
    mutable.

    Args:
        item:
            The object to thaw. Can be immutable, mutable, or implement the
            Thawable protocol.

    Returns:
        A mutable version of the input object. For deeply nested structures,
        the conversion is performed recursively.

    Raises:
        ThawError:
            If the object cannot be thawed and is not recognized as mutable or
            immutable.

    """
    if is_atom(item):
        return item

    if isinstance(item, Thawable):
        frozen = item.__thaw__()
        return thaw(frozen)

    return _thaw(item)

@singledispatch
def _thaw(item: object) -> object:
    """Dispatcher for the thawing objects."""
    if is_immutable(item):
        return item

    if is_mutable(item):
        return item

    raise ThawError(error_msg.type_error(type(item).__name__))


@_thaw.register(deque)
def _(data: deque[object]) -> deque[object]:
    """Thaw the contents of a deque.

    Recursively thaws all items inside the deque and returns a new deque.

    """
    return deque(thaw(item) for item in data)


@_thaw.register(dict)
def _(data: dict[object, object]) -> dict[object, object]:
    """Thaw the contents of a dictionary.

    Recursively thaws all values.

    """
    return {k: thaw(v) for k, v in data.items()}


@_thaw.register(frozenset)
def _(data: frozenset[object]) -> set[object]:
    """Thaw a frozenset into a set.

    Recursively thaws all values.

    """
    return set(map(thaw, data))


@_thaw.register(list)
def _(data: list[object]) -> list[object]:
    """Thaw the contents of a list and return a list.

    Recursively thaws all values.

    """
    return [thaw(item) for item in data]


@_thaw.register(set)
def _(data: set[object]) -> set[object]:
    """Thaw the contents of a set.

    Recursively thaws all values.

    """
    return {thaw(item) for item in data}


@_thaw.register(tuple)
def _(data: tuple[object]) -> list[object]:
    """Thaw a tuple and return a list.

    Recursively thaws all values.

    """
    return [thaw(item) for item in data]


@_thaw.register(Sequence)
def _(data: Sequence[object]) -> list[object]:
    """Thaw a Sequence (that isn't list/tuple/deque) into a mutable list.

    This is a catchall for other sequence types.

    """
    return [thaw(item) for item in data]


@_thaw.register(Mapping)
def _(data: Mapping[object, object]) -> dict[object, object]:
    """Thaw a Mapping and return a standard dictionary.

    Recursively thaws all values and returns a dictionary. This is a catchall
    for other mapping types.

    """
    return {k: thaw(v) for k, v in data.items()}
