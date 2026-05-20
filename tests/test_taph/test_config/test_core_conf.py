"""Tests for the taph.config.core_conf module."""
import datetime
import decimal
import fractions
import pathlib
import re
import uuid
from subprocess import CompletedProcess
from types import FunctionType, MethodType

from taph.config.core_conf import ATOMS, Atoms


def test_atoms_structural_integrity() -> None:
    """Verify that the ATOMS singleton is correctly instantiated with defaults."""
    assert isinstance(ATOMS, Atoms)
    assert ATOMS.decimal is decimal.Decimal
    assert ATOMS.fraction is fractions.Fraction
    assert ATOMS.uuid is uuid.UUID
    assert ATOMS.path is pathlib.PurePath
    assert ATOMS.process is CompletedProcess


def test_atoms_category_groups() -> None:
    """Verify separate explicit categorization groups within Atoms."""
    assert str in ATOMS.basic
    assert bool in ATOMS.basic
    assert bytes in ATOMS.basic
    assert type(None) in ATOMS.basic

    assert int in ATOMS.number
    assert float in ATOMS.number
    assert complex in ATOMS.number

    assert datetime.datetime in ATOMS.date
    assert datetime.date in ATOMS.date
    assert datetime.time in ATOMS.date
    assert datetime.timedelta in ATOMS.date

    assert re.Match in ATOMS.regex
    assert re.Pattern in ATOMS.regex

    assert FunctionType in ATOMS.func
    assert MethodType in ATOMS.func
    assert staticmethod in ATOMS.func
    assert classmethod in ATOMS.func
    assert property in ATOMS.func


def test_atoms_all_types_complete_path() -> None:
    """Verify all_types() aggregates every single category without exclusions."""
    all_types = ATOMS.all_types()

    expected_size = (
        len(ATOMS.basic)
        + len(ATOMS.number)
        + 1  # decimal
        + 1  # fraction
        + len(ATOMS.date)
        + 1  # uuid
        + 1  # path
        + len(ATOMS.regex)
        + 1  # process
        + len(ATOMS.func)
    )
    assert len(all_types) == expected_size

    assert type(None) in all_types
    assert complex in all_types
    assert pathlib.PurePath in all_types
    assert property in all_types


def test_atoms_numbers_subset_path() -> None:
    """Verify numbers() filters strictly to the numeric numeric/decimal/fraction subset."""
    nums = ATOMS.numbers()

    assert int in nums
    assert float in nums
    assert complex in nums
    assert decimal.Decimal in nums
    assert fractions.Fraction in nums

    assert str not in nums
    assert bool not in nums
    assert bytes not in nums
