"""Taph library core tools module.

This module contains low-level utilities for namespace parsing and type
inspection used across Taph's immutable data structures (Records, Manifests,
FrozenDicts).

"""

import typing
from collections.abc import MutableMapping, MutableSequence, MutableSet
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Container

    from taph.frozen_dict import FrozenDict

from taph.config.core_conf import ATOMS
from taph.protocols import Immutable

__all__: tuple[str, ...] = (
    'is_atom',
    'is_classvar',
    'is_immutable',
    'is_mutable',
    'namespace_skip',
    'snapshot',
)
_ATOMS: tuple[type, ...] = ATOMS.all_types()


def is_atom(value: object) -> bool:
    """Check if a value is a builtin immutable type.

    Args:
        value: An object to check if it is a builtin immutable type.

    Returns:
        True if the value given is an atomic type.

    """
    return isinstance(value, _ATOMS)


def is_classvar(hint: object) -> bool:
    """Check if a type hint is a ClassVar.

    Args:
        hint: A type annotation or object to inspect.

    Returns:
        True if the hint represents typing.ClassVar[...], False otherwise.

    """
    return hint is ClassVar or typing.get_origin(hint) is ClassVar


def is_immutable(value: object) -> bool:
    """Return true if the value is already deebly immutable.

    An object is considered immutable if it is a builtin immutable data type.
    Or if an object implements the Immutable protocol (has a __digest__).

    Args:
        value: The object to check for deep immutability

    Returns:
        True if the value is a builtin immutable type or has a __digest__.

    """
    if is_atom(value) or isinstance(value, Immutable):
        return True

    from taph.frozen_dict import FrozenDict  # noqa: PLC0415
    if isinstance(value, FrozenDict):
        return True

    return False


def is_mutable(value: object) -> bool:
    """Return True if the value is already mutable.

    Used by thaw() to avoid unnecessary work on mutable containers.

    Args:
        value: The object to check for mutability.

    Returns:
        True if the value is a mutable object type.

    """
    if isinstance(value, (dict, list, set)):
        return True

    return isinstance(
        value, (MutableMapping, MutableSequence, MutableSet)
    )


def namespace_skip(value: object, key: str = '') -> bool:
    """Return True if this (key, value) pair should be skipped as a data field.

    Args:
        value (object): Skip if value is a callable or function.
        key (str): Skip if the key is a dunder or abc field.

    Returns:
        True if the key, or value, are not data fields.

    """
    if (key.startswith('__') and key.endswith('__')) or key.startswith('_abc_'):
        return True

    if is_classvar(value):
        return True

    if isinstance(value, ATOMS.func) or callable(value):
        return True

    return False


def snapshot(
    obj: object, exclude: Container[str] = frozenset()
) -> FrozenDict[object, object]:
    """Create an immutable snapshot of an object's public state.

    Inspects `__dict__` (preferred) and `__slots__`. Only public, non-callable
    attributes are included. Values are recursively frozen.

    Useful for implementing `__freeze__` on custom classes or extracting state
    for Records/Manifests.

    Args:
        obj: Object to snapshot.
        exclude: Names of attributes to ignore (e.g. secrets, transient state).

    Returns:
        FrozenDict mapping attribute names to frozen values.

    """
    state = {}

    if hasattr(obj, '__dict__'):
        for key, value in obj.__dict__.items():
            if (
                not key.startswith('_')
                and key not in exclude
                and not callable(value)
            ):
                state[key] = value

    if hasattr(obj, '__slots__'):
        for slot in obj.__slots__:
            if (
                not slot.startswith('_')
                and slot not in exclude
                and slot not in state
            ):
                try:
                    value = getattr(obj, slot)
                    if not callable(value):
                        state[slot] = value
                except AttributeError:
                    continue

    from taph.frozen_dict import FrozenDict  # noqa: PLC0415
    return FrozenDict(state)
