"""Taph Testing Fixtures.

Provides centralized access to core Taph primitives for architectural
and behavioral unit testing.
"""
import pytest
from typing import Mapping, Any

from taph.record import Record
from taph.frozen_dict import FrozenDict
from taph.manifest import Manifest
from taph.tools.freeze_tools import freeze

# ---------------------------------------------------------
# Record Fixtures
# ---------------------------------------------------------

@pytest.fixture
def user_record_cls() -> Record:
    """Returns a concrete Record subclass with strictly enforced slots."""
    class User(Record):
        __slots__ = ('user_id', 'email', 'is_active')

        user_id: int
        email: str
        is_active: bool

    return User

@pytest.fixture
def sample_record(user_record_cls) -> Record:
    """Returns an instantiated, frozen Record."""
    return user_record_cls(user_id=101, email="arch@taph.io", is_active=True)

# ---------------------------------------------------------
# Mapping & Collection Fixtures
# ---------------------------------------------------------

@pytest.fixture
def sample_frozen_dict() -> FrozenDict[str, int]:
    """Returns a pre-populated FrozenDict using the fast-path constructor."""
    data = {"alpha": 1, "beta": 2, "gamma": 3}
    return FrozenDict.fromdict(data)

@pytest.fixture
def nested_mutable_data() -> dict[str, Any]:
    """Returns a deeply nested mutable structure for testing freeze()."""
    return {
        "metadata": {"version": 1, "tags": ["prod", "immutable"]},
        "records": [
            {"id": 1, "val": "A"},
            {"id": 2, "val": "B"}
        ],
        "flags": {True, False}
    }

# ---------------------------------------------------------
# Manifest Fixtures
# ---------------------------------------------------------

@pytest.fixture
def user_manifest(sample_record) -> Manifest:
    """Returns a Manifest containing multiple records."""
    return Manifest([
        sample_record,
        # Create a second record of the same type
        type(sample_record)(user_id=102, email="ops@taph.io", is_active=False)
    ])

# ---------------------------------------------------------
# Meta/Constraint Fixtures
# ---------------------------------------------------------

@pytest.fixture
def class_factory() -> Any:
    """Return a factory function to create dynamic Taph components.

    Used for testing metaclass validation (e.g., ensuring __slots__ enforcement).
    """
    def _create_record(name: str, slots: tuple[str, ...], **annotations: Any):
        # Dynamically construct a Record class
        return type(name, (Record,), {"__slots__": slots, "__annotations__": annotations})

    return _create_record

@pytest.fixture
def namespace_fixture() -> type:
    """Fixture for testing static Namespace containers."""
    from taph.meta.taph_meta import TaphType

    class SystemConfig(metaclass=TaphType):
        __slots__ = ()
        API_VERSION = "v2"
        TIMEOUT = 30

    return SystemConfig

# ---------------------------------------------------------
# Comparison & Tooling Fixtures
# ---------------------------------------------------------

@pytest.fixture
def benchmark_data() -> dict[str, int]:
    """Provides a large dataset for O(log N) bisection performance testing."""
    return {f"key_{i}": i for i in range(1000)}
