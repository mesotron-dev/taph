"""Validation utilities for slot names and canonical ordering.

These helpers ensure safe and consistent __slots__ definitions for slotted
immutable classes in Taph.

"""

import keyword
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection

__all__: tuple[str, ...] = ('canonical_slots', 'is_valid_slot')


def is_valid_slot(name: object) -> bool:
    """Determine if a value is suitable as a __slots__ entry.

    Valid slot names must:
    - Be non-empty strings
    - Be valid Python identifiers
    - Not be Python keywords
    - Not start with underscore (private/reserved)

    Args:
        name (str): Candidate slot name.

    Returns:
        True if the name is valid for __slots__, False otherwise.

    """
    return (
        isinstance(name, str)
        and name.isidentifier()
        and not keyword.iskeyword(name)
        and not name.startswith('_')
    )


def canonical_slots(slots: Collection[str]) -> tuple[str, ...]:
    """Sort and deduplicate a collection of slot names into a canonical tuple.

    Ensure deterministic layout/order for hashing, equality, and manifest
    generation.

    Args:
        slots: Iterable of valid slot name strings.

    Returns:
        Sorted tuple of unique slot names.

    """
    return tuple(sorted(set(slots)))
