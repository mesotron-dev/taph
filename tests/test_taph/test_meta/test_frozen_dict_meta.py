"""Tests for the taph.meta.frozen_dict_meta module (FrozenDictType)."""

import pytest
from collections.abc import Mapping
from taph.frozen_dict import FrozenDict
from taph.meta.frozen_dict_meta import FrozenDictType, _builder


def test_frozen_dict_meta_builder_empty() -> None:
    """Verify compilation returns empty tuples and safe digests when mapping is empty."""
    digest_index, keys, values, digest = _builder(None)
    assert digest_index == ()
    assert keys == ()
    assert values == ()
    assert isinstance(digest, bytes)

    digest_index2, keys2, values2, digest2 = _builder({})
    assert digest_index2 == ()
    assert keys2 == ()
    assert values2 == ()
    assert isinstance(digest2, bytes)


def test_frozen_dict_meta_builder_sorting_and_hashing() -> None:
    """Verify parallel sorting and consistent hashing calculations."""
    data = {'omega': 24, 'alpha': 1}
    digest_index, keys, values, digest = _builder(data)

    assert len(digest_index) == 2
    assert digest_index[0][0] <= digest_index[1][0]

    assert len(keys) == 2
    assert len(values) == 2
    assert isinstance(digest, bytes)


def test_frozen_dict_type_new_configuration() -> None:
    """Verify slots configuration and immutability attributes are correctly bound."""
    class TestDict(metaclass=FrozenDictType):
        pass

    assert TestDict.__slots__ == ('_index_', '_keys_', '_values_', '__digest__')
    assert TestDict.__setattr__ == FrozenDictType._block_setattr
    assert TestDict.__delattr__ == FrozenDictType._block_delattr


def test_frozen_dict_type_call_branches() -> None:
    """Test call routing based on mapping input and presence of keyword args."""
    fd1 = FrozenDict({'a': 1})
    assert fd1['a'] == 1

    fd2 = FrozenDict({'a': 1}, b=2)
    assert fd2['a'] == 1
    assert fd2['b'] == 2

    fd3 = FrozenDict([('a', 1), ('b', 2)])
    assert fd3['a'] == 1
    assert fd3['b'] == 2

    fd4 = FrozenDict()
    assert len(fd4) == 0

    fd5 = FrozenDict(a=1, b=2)
    assert fd5['a'] == 1
    assert fd5['b'] == 2

    with pytest.raises(TypeError):
        FrozenDict({'a': 1}, {'b': 2})
