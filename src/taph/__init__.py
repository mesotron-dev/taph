"""Taph: A library for Immutable objects."""

from taph.core import Immutable, Namespace, freeze, is_immutable
from taph.exceptions import ImmutableError, TaphError

__version__ = '0.1.0'
__all__ = (
    'Namespace',
    'Immutable',
    'ImmutableError',
    'TaphError',
    'is_immutable',
    'freeze',
)
