"""Tests for the taph.protocols module."""

from typing import ClassVar
import pytest

from taph.protocols import Freezable, Freeze, Immutable, Thawable, Thaw
from taph.frozen_dict import FrozenDict
from taph.record import Record
from taph.tools.freeze_tools import freeze
from taph.tools.thaw_tools import thaw

# ---------------------------------------------------------
# Conformance Mock Objects
# ---------------------------------------------------------

class CustomFreezable:
    """Conforms to the Freezable protocol."""
    def __init__(self, value: int) -> None:
        self.value = value

    def __freeze__(self) -> int:
        return self.value

class CustomImmutable:
    """Conforms to the Immutable protocol."""
    def __init__(self, digest: bytes) -> None:
        self.__digest__ = digest

    @property
    def fingerprint(self) -> str:
        return "mock_fingerprint"

    @property
    def hexdigest(self) -> str:
        return "mock_hexdigest"

class CustomThawable:
    """Conforms to the Thawable protocol."""
    def __init__(self, value: object) -> None:
        self.value = value

    def __thaw__(self) -> object:
        return self.value

class NonConforming:
    """Fails all structural protocol validations."""
    pass

# ---------------------------------------------------------
# Protocol Verification Tests
# ---------------------------------------------------------

def test_freezable_protocol_conformance() -> None:
    """Verify runtime identification of the Freezable protocol."""
    # Positive case
    freezable_inst = CustomFreezable(42)
    assert isinstance(freezable_inst, Freezable) is True

    # Negative case
    assert isinstance(NonConforming(), Freezable) is False
    assert isinstance(42, Freezable) is False


def test_immutable_protocol_conformance(sample_record, sample_frozen_dict) -> None:
    """Verify runtime identification of the Immutable protocol."""
    # Custom conforming instance
    immutable_inst = CustomImmutable(b"crypt_digest_16b")
    assert isinstance(immutable_inst, Immutable) is True

    # Core Taph Types conforming to Immutable
    assert isinstance(sample_record, Immutable) is True
    assert isinstance(sample_frozen_dict, Immutable) is True

    # Check correct attribute access via interface
    assert sample_record.__digest__ is not None
    assert isinstance(sample_record.fingerprint, str)
    assert isinstance(sample_record.hexdigest, str)

    # Negative case
    assert isinstance(NonConforming(), Immutable) is False
    assert isinstance([1, 2, 3], Immutable) is False


def test_thawable_protocol_conformance(sample_frozen_dict, sample_record) -> None:
    """Verify runtime identification of the Thawable protocol."""
    # Custom conforming instance
    thawable_inst = CustomThawable([1, 2])
    assert isinstance(thawable_inst, Thawable) is True

    # Core Taph Types conforming to Thawable
    assert isinstance(sample_frozen_dict, Thawable) is True

    # Negative cases
    assert isinstance(NonConforming(), Thawable) is False
    assert isinstance(sample_record, Thawable) is False  # Records are terminal; cannot be thawed directly


def test_functional_type_conformance_simulation() -> None:
    """Verify that freeze and thaw align with structural functional signatures."""
    # Validate conforming callable wrappers
    def execute_freezer(freezer: Freeze, obj: object) -> object:
        return freezer(obj)

    def execute_thawer(thawer: Thaw, obj: object) -> object:
        return thawer(obj)

    # Simulated runtime static-type checking loop
    frozen_res = execute_freezer(freeze, [10, 20])
    assert frozen_res == (10, 20)

    thawed_res = execute_thawer(thaw, (10, 20))
    assert thawed_res == [10, 20]
