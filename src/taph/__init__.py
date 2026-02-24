"""Taph: A library for Record objects."""

from taph.exceptions import (
    FrozenDictError,
    ImmutableError,
    ManifestError,
    RecordError,
    TaphError,
)
from taph.frozen_dict import FrozenDict
from taph.manifest import Manifest
from taph.record import Record

__version__ = '0.1.2'
__all__ = (
    'FrozenDict',
    'FrozenDictError',
    'ImmutableError',
    'Manifest',
    'ManifestError',
    'Record',
    'RecordError',
    'TaphError',
)
