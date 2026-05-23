"""Tests for the taph.record module, ensuring complete coverage."""

import copy
import pytest

from taph.exceptions import ImmutableError, RecordError
from taph.protocols import Immutable
from taph.record import Record


class User(Record):
    """A concrete Record subclass for testing."""

    __slots__ = ('uid', 'name', 'is_active')
    uid: int
    name: str
    is_active: bool


class Point(Record):
    """Another concrete Record subclass for testing."""

    __slots__ = ('x', 'y')
    x: float
    y: float


def test_record_creation_and_access() -> None:
    """Verify basic instantiation and attribute access."""
    user = User(uid=1, name='Alice', is_active=True)
    assert user.uid == 1
    assert user.name == 'Alice'
    assert user.is_active is True
    assert user['uid'] == 1
    assert user.get('name') == 'Alice'
    assert user.get('missing', 'default') == 'default'


def test_record_contains() -> None:
    """Verify records __contains__ method.

    Expression: key != taph.digest and key in self.__class__.__slots__
    """
    user = User(uid=1, name='Alice', is_active=True)

    assert 'uid' in user
    assert '__digest__' not in user
    assert 'non_existent' not in user


def test_record_copy() -> None:
    """Verify that copy and deepcopy behave correctly for immutable Record."""
    user = User(uid=1, name='Alice', is_active=True)

    assert copy.copy(user) is user
    assert copy.deepcopy(user) is user
    memo: dict[int, object] = {}
    assert user.__deepcopy__(memo) is user


def test_record_dir() -> None:
    """Verify that dir() returns slots and public attributes, excluding digest."""
    user = User(uid=1, name='Alice', is_active=True)
    directory = dir(user)

    assert 'uid' in directory
    assert 'name' in directory
    assert 'is_active' in directory
    assert '__digest__' not in directory
    assert 'keys' in directory


def test_record_eq_ne() -> None:
    """Verify __eq__ and __ne__ methods."""
    u1 = User(uid=1, name='Alice', is_active=True)
    u2 = User(uid=1, name='Alice', is_active=True)
    u3 = User(uid=2, name='Bob', is_active=False)

    assert u1 == u1
    assert u1 == u2
    assert u1 != u3
    assert (u1 == u3) is False
    assert u1.__eq__('not_an_immutable') is NotImplemented


def test_record_getitem() -> None:
    """Verify __getitem__."""
    user = User(uid=1, name='Alice', is_active=True)

    with pytest.raises(KeyError):
        _ = user['__digest__']

    assert user['uid'] == 1

    with pytest.raises(KeyError):
        _ = user['non_existent']


def test_record_hash() -> None:
    """Verify stable, content-based hash is derived from digest."""
    u1 = User(uid=1, name='Alice', is_active=True)
    u2 = User(uid=1, name='Alice', is_active=True)
    u3 = User(uid=2, name='Bob', is_active=False)

    assert hash(u1) == hash(u2)
    assert hash(u1) != hash(u3)


def test_record_replace() -> None:
    """Verify __replace__ method."""
    user = User(uid=1, name='Alice', is_active=True)

    assert user.__replace__() is user

    updated = user.__replace__(name='Bob', is_active=False)
    assert updated.uid == 1
    assert updated.name == 'Bob'
    assert updated.is_active is False
    assert updated is not user


def test_record_repr() -> None:
    """Verify clear and descriptive __repr__ format."""
    user = User(uid=1, name='Alice', is_active=True)
    assert repr(user) == "User(uid=1, name='Alice', is_active=True)"


def test_record_from_dict() -> None:
    """Verify MC/DC on from_dict method."""
    with pytest.raises(RecordError, match='Missing required fields'):
        User.from_dict({'uid': 1})

    user = User.from_dict({
        'uid': 2,
        'name': 'Bob',
        'is_active': False,
        'extra_key': 'ignored',
    })
    assert user.uid == 2
    assert user.name == 'Bob'
    assert user.is_active is False


def test_record_subclasshook() -> None:
    """Verify MC/DC on __subclasshook__."""
    class VirtualRecord:
        __slots__ = ('x', '__digest__')

    assert issubclass(VirtualRecord, Record) is True

    class VirtualNonRecord:
        __slots__ = ('x', 'y')

    assert issubclass(VirtualNonRecord, Record) is False

    class EmptyClass:
        pass

    assert issubclass(EmptyClass, Record) is False

    assert issubclass(VirtualRecord, User) is False


def test_record_fromkeys() -> None:
    """Verify that fromkeys is not implemented for Record."""
    with pytest.raises(NotImplementedError):
        User.fromkeys(['uid'])


def test_record_blocked_mutations() -> None:
    """Verify all mapping mutation attempts raise ImmutableError."""
    user = User(uid=1, name='Alice', is_active=True)

    with pytest.raises(ImmutableError):
        user.pop('uid')

    with pytest.raises(ImmutableError):
        user.popitem()

    with pytest.raises(ImmutableError):
        user.update({'uid': 2})

    with pytest.raises(ImmutableError):
        user.setdefault('uid', 5)


def test_record_immutability_setattr_delattr() -> None:
    """Verify strict instance immutability protects attributes."""
    user = User(uid=1, name='Alice', is_active=True)

    with pytest.raises(ImmutableError):
        user.name = 'Bob'

    with pytest.raises(ImmutableError):
        del user.uid


def test_record_properties() -> None:
    """Verify content fingerprinting and hexdigest conversion."""
    user = User(uid=1, name='Alice', is_active=True)
    assert isinstance(user.fingerprint, str)
    assert isinstance(user.hexdigest, str)


def test_record_pop_explicit() -> None:
    """Verify explicit pop calls raise ImmutableError with structured messaging."""
    user = User(uid=1, name='Alice', is_active=True)
    with pytest.raises(ImmutableError) as exc_info:
        user.pop('uid')
    assert "Cannot remove" in str(exc_info.value)


def test_record_inheritance_empty_base() -> None:
    """Verify MRO resolution and field aggregation when inheriting from empty Records."""
    class EmptyBase(Record):
        __slots__ = ()

    class ChildOfEmpty(EmptyBase):
        __slots__ = ("x",)
        x: int

    inst = ChildOfEmpty(x=42)
    assert inst.x == 42


def test_record_eq_ne_conformance() -> None:
    """Verify that Record.__ne__ propagates NotImplemented without evaluating truthiness."""
    u1 = User(uid=1, name='Alice', is_active=True)
    u3 = User(uid=2, name='Bob', is_active=False)

    assert u1.__ne__(u3) is True

    # Assert correct Python 3.14 compliant propagation
    assert u1.__ne__('not_an_immutable') is NotImplemented


def test_record_explicit_introspection_dunders(sample_record):
    """Cover statement execution boundaries inside Record custom directory maps."""
    assert "user_id" in sample_record.__dir__()
    assert sample_record.__copy__() is sample_record


def test_record_popitem_and_setdefault_direct(sample_record):
    """Directly call popitem and setdefault on Record to cover the raise statements."""
    with pytest.raises(ImmutableError):
        sample_record.popitem()

    with pytest.raises(ImmutableError):
        sample_record.setdefault('user_id', 999)


def test_record_direct_iteration(sample_record) -> None:
    """Verify that direct iteration over a Record yields field names in order (covers line 140)."""
    fields = list(sample_record)
    assert fields == ['user_id', 'email', 'is_active']
