"""Tests for Taph validation utilities."""

import keyword
from typing import ClassVar
import pytest
from taph.tools.validation_tools import canonical_slots, is_valid_slot


def test_is_valid_slot_mcdc() -> None:
    """Full test suite for is_valid_slot."""
    assert is_valid_slot("valid_slot_name") is True
    assert is_valid_slot(123) is False
    assert is_valid_slot("slot-with-hyphen") is False
    assert is_valid_slot("class") is False
    assert is_valid_slot("_private_slot") is False


def test_is_valid_slot_edge_cases() -> None:
    """Verify edge cases outside of standard identifier mappings."""
    assert is_valid_slot("") is False
    assert is_valid_slot("slot name") is False
    assert is_valid_slot("1slot") is False


def test_canonical_slots() -> None:
    """Verify deduplication and deterministic sorting of slots."""
    assert canonical_slots([]) == ()
    input_slots = ["values", "index", "keys", "values", "digest"]
    expected_order = ("digest", "index", "keys", "values")
    assert canonical_slots(input_slots) == expected_order
    set_slots = {"z", "a", "m"}
    assert canonical_slots(set_slots) == ("a", "m", "z")
    generator_slots = (s for s in ["field_b", "field_a"])
    assert canonical_slots(generator_slots) == ("field_a", "field_b")
