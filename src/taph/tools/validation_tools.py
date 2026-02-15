"""The Validation Tools module provides utility functions for Taph.

#TODO

"""

import keyword
from collections.abc import Collection

__all__: tuple[str, ...] = ('is_valid_slot', 'canonical_slots')


def is_valid_slot(name: object) -> bool:
    """Check if a name can be used as a __slots__ entry.

    Requirements:
        1. Must be a string.
        2. Must be a valid Python identifier.
        3. Must not be a Python keyword.
        4. Must not start with underscore.

    Args:
        name(str): The string to validate.

    Returns:
        True if the string can be a slot name, False otherwise.

    """
    if not isinstance(name, str):
        return False
    if len(name) == 0:
        return False
    if name.isspace():
        return False
    if keyword.iskeyword(name):
        return False
    if name.startswith('_'):
        return False
    return True


def canonical_slots(slots: Collection[str]) -> tuple[str, ...]:
    """Return a sorted & canonical ordering of slots (strings).

    Enables consistent slot layout for FrozenDict, Namespace, & Immutable.

    Args:
        slots(str): A collection of valid strings for use in __slots__.

    Returns:
        A sorted tuple of strings for __slots__.

    """
    return tuple(sorted(slots))
