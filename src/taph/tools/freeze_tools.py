"""Utilities for deep immutability and object freezing.

This module provides the core `freeze` function (singledispatch) and `snapshot`
helper to convert mutable objects/structures into deeply immutable equivalents,
respecting the `Freezable` protocol where implemented.

"""

from collections import deque
from collections.abc import Mapping, Sequence
from functools import singledispatch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taph.frozen_dict import FrozenDict
from taph.config.tools_conf import freeze_error_messages as error_msg
from taph.exceptions import ImmutableError
from taph.protocols import Freezable
from taph.tools.core_tools import is_immutable

__all__: tuple[str] = ('freeze',)


def freeze(item: object) -> object:
    """Transform an item into a deeply immutable equivalent.

    - Basic immutable Python builtin types are returned unchanged
    - Mutable containers (list, dict, set) are recursively frozen
    - Objects with `__freeze__()` method use that (via Freezable protocol)
    - Already immutable objects are returned as-is
    - Cycles are detected and raise ImmutableError

    This function is used by Records, Manifests, and FrozenDict to ensure
    content stability and hash safety.

    Args:
        item: Any Python object.

    Returns:
        An immutable version (tuple, frozenset, FrozenDict, or same object).

    Raises:
        ImmutableError: If a cycle is detected or the object cannot be frozen.
        TypeError: If no conversion path exists.

    """
    if is_immutable(item):
        return item

    if isinstance(item, Freezable):
        result = item.__freeze__()
        if is_immutable(result):
            return result
        return freeze(result)

    return _freezer(item)

@singledispatch
def _freezer(item: object) -> object:
    """Dispatcher for the freeze function."""
    raise ImmutableError(error_msg.freeze(type(item).__name__))


@_freezer.register(deque)
def _(deque_object: deque[object]) -> tuple[object, ...]:
    """Freeze a deque sequence into a tuple."""
    return tuple(freeze(item) for item in deque_object)


@_freezer.register(dict)
def _(dict_object: dict[object, object]) -> FrozenDict[object, object]:
    """Freeze a dict type into a FrozenDict."""
    from taph.frozen_dict import FrozenDict  # noqa: PLC0415

    return FrozenDict(dict_object)


@_freezer.register(frozenset)
def _(frozenset_object: frozenset[object]) -> frozenset[object]:
    """Return unchanged if all items are immutable, else freeze recursively."""
    if all(is_immutable(x) for x in frozenset_object):
        return frozenset_object
    return frozenset(freeze(item) for item in frozenset_object)


@_freezer.register(list)
def _(list_object: list[object]) -> tuple[object, ...]:
    """Freeze a list into a tuple (recursive)."""
    return tuple(freeze(item) for item in list_object)


@_freezer.register(set)
def _(set_object: set[object]) -> frozenset[object]:
    """Freeze a set into a frozenset."""
    return frozenset(freeze(item) for item in set_object)


@_freezer.register(tuple)
def _(tuple_object: tuple[object]) -> tuple[object, ...]:
    """Return unchanged if all items are immutable, else recursively freeze."""
    if all(is_immutable(x) for x in tuple_object):
        return tuple_object
    return tuple(freeze(item) for item in tuple_object)


@_freezer.register(Mapping)
def _(mapping_object: Mapping[object, object]) -> FrozenDict[object, object]:
    """Freeze a dict into a FrozenDict."""
    from taph.frozen_dict import FrozenDict  # noqa: PLC0415
    return FrozenDict(mapping_object)


@_freezer.register(Sequence)
def _(sequence_object: Sequence[object]) -> tuple[object, ...]:
    """Catch other types of sequences not explicitly defined."""
    return tuple(freeze(item) for item in sequence_object)
