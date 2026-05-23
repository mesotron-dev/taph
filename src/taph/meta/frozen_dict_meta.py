"""The FrozenDict Metaclass Factory module."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

    from taph.frozen_dict import FrozenDict

from taph.config.meta_conf import frozen_dict_conf as frozen_dict
from taph.meta.taph_meta import TaphType
from taph.tools.freeze_tools import freeze
from taph.tools.hash_tools import hash_mapping, mk_digest

__all__: tuple[str] = ('FrozenDictType',)


def _builder(data: Mapping[object, object] | None) -> tuple[object, ...]:
    """Build up a new frozen dictionary."""
    digest_index: list[tuple[bytes, int]] = []
    items: list[tuple[object, bytes, object, bytes]] = []
    if data:
        for k, v in enumerate(data.items()):
            index, item = k, v
            frozen_key, frozen_value = freeze(item[0]), freeze(item[1])
            key_digest, value_digest = (
                mk_digest(frozen_key),
                mk_digest(frozen_value),
            )
            digest_index.append((key_digest, index))
            items.append((frozen_key, key_digest, frozen_value, value_digest))
        digest_index.sort(key=lambda x: x[0])
        keys, key_digests, values, value_digests = zip(*items, strict=True)
        digest = hash_mapping(
            len(items), zip(key_digests, value_digests, strict=True)
        )
    else:
        keys, key_digests, values, value_digests = (), (), (), ()
        digest = hash_mapping(0, ())
    return (tuple(digest_index), keys, values, digest)


class FrozenDictType(TaphType):
    """Metaclass for immutable dictionary instances."""

    __slots__ = ()

    def __new__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, object]
    ) -> type:
        """Create a new FrozenDict class."""
        # py3.12+ generic syntax leaks non-string keys
        namespace = {k: v for k, v in namespace.items() if isinstance(k, str)}

        namespace[frozen_dict.slots] = (
            frozen_dict.index_attr,
            frozen_dict.keys,
            frozen_dict.values,
            frozen_dict.digest,
        )
        namespace[frozen_dict.set_attr] = TaphType._block_setattr
        namespace[frozen_dict.del_attr] = TaphType._block_delattr

        return super().__new__(cls, name, bases, namespace)

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Manage the creation of the FrozenDict."""
        cls = cast('type', self)
        if len(args) == 1 and isinstance(args[0], cls) and not kwargs:
            return args[0]
        data: dict[object, object] = cast(
            'dict[object, object]',
            dict(*args, **kwargs)
        )

        digest_index, keys, values, digest = _builder(data)
        instance: FrozenDict[object, object] = object.__new__(
            cast('type', self)
        )
        object.__setattr__(instance, frozen_dict.index_attr, digest_index)
        object.__setattr__(instance, frozen_dict.keys, keys)
        object.__setattr__(instance, frozen_dict.values, values)
        object.__setattr__(instance, frozen_dict.digest, digest)

        return instance
