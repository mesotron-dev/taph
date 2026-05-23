"""Tests for the taph.frozen_dict module."""

import copy
import pytest
from taph.frozen_dict import FrozenDict
from taph.exceptions import ImmutableError
from taph.config.meta_conf import taph_type_conf as taph

def test_frozendict_creation_and_access(sample_frozen_dict):
    """Verify instantiation via the metaclass __call__ bypass."""
    assert sample_frozen_dict['alpha'] == 1
    assert sample_frozen_dict.get('beta') == 2
    assert sample_frozen_dict.get('missing', 'default') == 'default'
    empty = FrozenDict()
    assert len(empty) == 0

    # ??
    assert sample_frozen_dict.get(taph.digest, 'blocked') == 'blocked'

    with pytest.raises(KeyError):
        _ = sample_frozen_dict['omega']


def test_frozendict_immutability(sample_frozen_dict):
    """Verify metaclass protections on instances."""
    with pytest.raises(TypeError, match="does not support item assignment"):
        sample_frozen_dict['gamma'] = 4

    with pytest.raises(TypeError, match="does not support item deletion"):
        del sample_frozen_dict['alpha']


def test_frozendict_contains_and_iter(sample_frozen_dict):
    """Verify membership testing and iteration logic."""
    assert ('alpha' in sample_frozen_dict) is True
    assert ('omega' in sample_frozen_dict) is False
    with pytest.raises(KeyError):
        _ = sample_frozen_dict['omega']

    keys = list(sample_frozen_dict)
    assert keys == ['alpha', 'beta', 'gamma']
    assert len(sample_frozen_dict) == 3


def test_frozendict_combinatorics():
    """Verify dict merging (| operator) returns a new FrozenDict."""
    fd1 = FrozenDict({'a': 1, 'b': 2})
    fd2 = FrozenDict({'b': 99, 'c': 3})

    merged = fd1 | fd2
    assert isinstance(merged, FrozenDict)
    assert merged['a'] == 1
    assert merged['b'] == 99
    assert merged['c'] == 3
    assert merged.__or__(42) is NotImplemented

    rmerged = fd2 | fd1
    assert isinstance(rmerged, FrozenDict)
    assert rmerged['a'] == 1
    assert rmerged['b'] == 2
    assert rmerged['c'] == 3
    assert rmerged.__ror__(42) is NotImplemented
    dict_merged = {'a': 42} | rmerged
    assert isinstance(dict_merged, FrozenDict)
    assert dict_merged['a'] == 1
    assert dict_merged['b'] == 2
    assert dict_merged['c'] == 3


def test_frozendict_blocked_mutations(sample_frozen_dict):
    """Verify dictionary mutation methods are safely sealed."""
    with pytest.raises(ImmutableError):
        sample_frozen_dict.pop('alpha')
    with pytest.raises(ImmutableError):
        sample_frozen_dict.popitem()
    with pytest.raises(ImmutableError):
        sample_frozen_dict.clear()
    with pytest.raises(TypeError):
        sample_frozen_dict.setdefault('delta', 4)
    with pytest.raises(TypeError):
        sample_frozen_dict.update({'d': 4})


def test_frozendict_freezable_thawable_protocols(sample_frozen_dict):
    """Verify the integration with Freezable and Thawable protocols."""
    assert sample_frozen_dict.__freeze__() is sample_frozen_dict
    assert sample_frozen_dict.copy() is sample_frozen_dict

    thawed = sample_frozen_dict.__thaw__()
    assert type(thawed) is dict
    assert thawed['alpha'] == 1


def test_frozendict_subclass_prevention():
    """Verify Terminal Type inheritance lock."""
    with pytest.raises(TypeError, match="Cannot subclass immutable mapping"):
        class ChildDict(FrozenDict):
            pass

def test_frozendict_identity_hashing(sample_frozen_dict):
    """Verify content hashing and distinct structure."""
    assert isinstance(hash(sample_frozen_dict), int)
    clone = FrozenDict(sample_frozen_dict)
    assert sample_frozen_dict == clone
    assert hash(sample_frozen_dict) == hash(clone)
    assert sample_frozen_dict != FrozenDict({'alpha': 1})
    assert sample_frozen_dict.__eq__(100) is NotImplemented
    assert sample_frozen_dict.__ne__(100) is NotImplemented


def test_frozendict_layout(sample_frozen_dict):
    """Verify system instrospection and sizing."""
    attributes = dir(sample_frozen_dict)
    assert '_keys_' not in attributes
    assert '_values_' not in attributes
    assert '_index_' not in attributes
    assert sample_frozen_dict.__sizeof__() > 0
    assert isinstance(sample_frozen_dict.fingerprint, str)
    assert isinstance(sample_frozen_dict.hexdigest, str)


def test_frozendict_contains_digest(sample_frozen_dict) -> None:
    """Verify that checking membership of taph.digest raises KeyError."""
    with pytest.raises(KeyError):
        _ = '__digest__' in sample_frozen_dict


def test_frozendict_deepcopy(sample_frozen_dict) -> None:
    """Verify that deepcopy returns the immutable instance and populates memo."""
    memo: dict[int, object] = {1: '1'}
    assert copy.deepcopy(sample_frozen_dict, memo) is sample_frozen_dict
    assert copy.deepcopy(sample_frozen_dict) is sample_frozen_dict


def test_frozenset_copy(sample_frozen_dict) -> None:
    """Verify that copy returns the immutable instance."""
    fc = copy.copy(sample_frozen_dict)
    assert fc is sample_frozen_dict


def test_frozendict_eq_fallback_explicit(sample_frozen_dict) -> None:
    """Explicitly verify high-performance equality branches."""
    assert sample_frozen_dict.__eq__(100) is NotImplemented
    assert sample_frozen_dict.__ne__(100) is NotImplemented


def test_frozendict_union_operator_fallbacks(sample_frozen_dict) -> None:
    """Verify union operator fallbacks when evaluated against mismatched types."""
    assert sample_frozen_dict.__or__(42) is NotImplemented
    assert sample_frozen_dict.__ror__(42) is NotImplemented


def test_frozendict_dir_and_bisection_boundaries(sample_frozen_dict):
    """Cover __dir__ collection array and high-boundary bisection lookups."""
    assert "__init__" in sample_frozen_dict.__dir__()

    for i in range(500):
        high_key = f"zzzz_boundary_key_{i}"
        assert (high_key in sample_frozen_dict) is False
        assert sample_frozen_dict.get(high_key) is None


def test_frozendict_eq_comprehensive(sample_frozen_dict):
    """Test __eq__ digest fast-path, mapping fallback, and length check."""
    clone = FrozenDict(sample_frozen_dict)
    different = FrozenDict({'alpha': 999})

    assert sample_frozen_dict == clone
    assert sample_frozen_dict != different

    assert sample_frozen_dict == {'alpha': 1, 'beta': 2, 'gamma': 3}
    assert sample_frozen_dict != {'alpha': 1}
    assert sample_frozen_dict != {'alpha': 1, 'beta': 2, 'extra': 99}
    assert not sample_frozen_dict.__eq__({'a': 1})
    assert not sample_frozen_dict.__eq__({'a': 1, 'b': 2, 'c': 3, 'd': 4})
    assert sample_frozen_dict == {'alpha': 1, 'beta': 2, 'gamma': 3}
    assert sample_frozen_dict != {'alpha': 1, 'beta': 2, 'gamma': 999}
    assert sample_frozen_dict.__eq__(123) is NotImplemented
    assert sample_frozen_dict.__eq__(None) is NotImplemented

    assert sample_frozen_dict != different
    assert not (sample_frozen_dict != clone)


def test_frozendict_from_dict():
    """Cover FrozenDict.from_dict classmethod."""
    d = {'x': 10, 'y': 20}
    fd = FrozenDict.from_dict(d)

    assert fd == d
    assert fd == FrozenDict(d)
