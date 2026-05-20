"""Taph: A library for Record objects."""

from taph.exceptions import (
    FrozenDictError,
    ImmutableError,
    ManifestError,
    RecordError,
    TaphError,
    ThawError,
)
from taph.frozen_dict import FrozenDict
from taph.manifest import Manifest
from taph.record import Record
from taph.tools.freeze_tools import freeze
from taph.tools.thaw_tools import thaw

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
    'ThawError',
    'freeze',
    'thaw',
)
