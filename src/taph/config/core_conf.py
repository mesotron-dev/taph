"""Taph core configuration module."""

import datetime
import decimal
import fractions
import pathlib
import re
import uuid
from subprocess import CompletedProcess
from types import FunctionType, MethodType
from typing import NamedTuple

__all__: tuple[str, ...] = ('ATOMS',)


class Atoms(NamedTuple):
    """The basic types that may be frozen."""

    basic: tuple[type, ...] = (str, bool, bytes, type(None))
    number: tuple[type, ...] = (int, float, complex)
    decimal: type = decimal.Decimal
    fraction: type = fractions.Fraction
    date: tuple[type, ...] = (
        datetime.datetime,
        datetime.date,
        datetime.time,
        datetime.timedelta,
    )
    uuid: type = uuid.UUID
    path: type = pathlib.PurePath
    regex: tuple[type, ...] = (re.Match, re.Pattern)
    # enum: type = enum.Enum defer for now
    process: type = CompletedProcess
    func: tuple[type, ...] = (
        FunctionType,
        MethodType,
        staticmethod,
        classmethod,
        property,
    )

    def all_types(self) -> tuple[type, ...]:
        """Return all atoms."""
        return (
            *self.basic,
            *self.number,
            self.decimal,
            self.fraction,
            *self.date,
            self.uuid,
            self.path,
            *self.regex,
            self.process,
            *self.func,
        )

    def numbers(self) -> tuple[type, ...]:
        """Return all number types."""
        return (
            *self.number,
            self.decimal,
            self.fraction,
        )


ATOMS: Atoms = Atoms()
