"""The NamespaceMeta class module.

This module provides the metaclass factory for static Manifest containers,
ensuring that all attributes are frozen at class definition time and a
cryptographic content digest is permanently generated.

"""

import sys
from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import NotImplementedType

from taph.config.meta_conf import manifest_type_conf as manifest
from taph.meta.taph_meta import TaphType
from taph.tools.core_tools import namespace_skip
from taph.tools.freeze_tools import freeze
from taph.tools.hash_tools import content_id, hash_id, hex_id, mk_digest

__all__: tuple[str] = ('ManifestType',)


def _parse_namespace(
    namespace: dict[str, object],
) -> tuple[tuple[str, ...], tuple[object, ...], bytes | None]:
    """Parse a namespace to sort, freeze, & make a hash digest.

    Filters out:
    - dunder names (__xxx__ and xxx__)
    - callables (methods, functions)
    - special Taph markers (_taphgen_)
    - ATOMS.func instances

    Parse a namespace suitable for constructing a Manifest.

    Args:
        namespace: Dictionary to extract public, non-callable values from.

    Returns:
        Tuple of (sorted field names, frozen values in same order, BLAKE2b
        digest of the pair list). If namespace is empty or filtered to
        nothing, returns ((), (), None).

    """
    items: list[tuple[str, object]] = []
    for k, v in namespace.items():
        if namespace_skip(v, key=k):
            continue

        items.append((k, freeze(v)))

    if not items:
        return ((), (), mk_digest(None))
    items.sort(key=lambda x: x[0])
    data = tuple(items)
    digest: bytes = mk_digest(data)
    keys, values = zip(*data, strict=True)
    return (keys, values, digest)


class ManifestType(TaphType):
    """Metaclass for Static Containers."""

    __slots__ = ()

    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, object]
    ) -> type:
        """Create a new Manifest class."""
        if manifest.slots not in namespace:
            namespace[manifest.slots] = ()
        elif namespace[manifest.slots] != ():
            raise AttributeError(manifest.no_instance)

        (  # parse out keys, values, sort, freeze, make digest
            namespace[manifest.keys],
            namespace[manifest.values],
            namespace[manifest.digest],
        ) = _parse_namespace(namespace)

        namespace[manifest.match_args] = namespace[manifest.keys]
        namespace[manifest.set_attr] = TaphType._block_setattr
        namespace[manifest.del_attr] = TaphType._block_delattr

        return super().__new__(mcs, name, bases, namespace)

    def __call__(self, *args: object, **kwargs: object) -> object: # noqa: ARG002
        """Prevent instantiation of Manifest classes."""
        raise AttributeError(manifest.no_instance)

    def __contains__(self, key: str) -> bool:
        """#todo."""
        return key in getattr(self, manifest.keys, ())

    def __eq__(self, other: object) -> bool:
        """Compare equality based on the manifest digest."""
        other_digest = getattr(other, manifest.digest, None)
        if other_digest is not None:
            if getattr(self, manifest.digest) == getattr(
                other, manifest.digest, None
            ):
                return True
        return False

    def __getitem__(self, key: str) -> object:
        """#todo."""
        if key not in getattr(self, manifest.keys, ()):
            raise KeyError(key)
        return getattr(self, key)

    def __hash__(self) -> int:
        """Return a stable int hash."""
        return hash_id(getattr(self, manifest.digest))

    def __iter__(self) -> object:
        """#todo."""
        yield from zip(
            getattr(self, manifest.keys),
            getattr(self, manifest.values),
            strict=True,
        )

    def __len__(self) -> int:
        """#todo."""
        return len(getattr(self, manifest.keys, ()))

    def __ne__(self, other: object) -> bool | NotImplementedType:
        """Return self != other."""
        other_digest = getattr(other, manifest.digest, None)
        if other_digest is not None:
            if getattr(self, manifest.digest) != getattr(
                other, manifest.digest
            ):
                return True
            return False
        return NotImplemented

    def __or__(self, other: object) -> type | NotImplementedType:  # type: ignore[override] #
        """Return self | other."""
        if not isinstance(other, Mapping):
            return NotImplemented

        data: dict[str, object] = dict(
            zip(
                getattr(self, manifest.keys, ()),
                getattr(self, manifest.values, ()),
                strict=True,
            )
        )
        data.update(other)

        return cast('type', self(data, name=self.__name__))

    def __repr__(self) -> str:
        count = len(getattr(self, manifest.values, ()))
        data = dict(
            zip(
                getattr(self, manifest.keys),
                getattr(self, manifest.values),
                strict=True,
            )
        )
        return f'length: {count}; data: {data}'

    def __ror__(self, other: object) -> type | NotImplementedType:  # type: ignore[override] #
        """Return self | other."""
        if not isinstance(other, Mapping):
            return NotImplemented

        data = dict(other)
        data.update(
            dict(
                zip(
                    getattr(self, manifest.keys, ()),
                    getattr(self, manifest.values, ()),
                    strict=True,
                )
            )
        )

        return cast('type', self(data, name=self.__name__))

    def __sizeof__(self) -> int:
        """Return the size of the Manifest in bytes."""
        size = super().__sizeof__()
        size += sys.getsizeof(getattr(self, manifest.digest))
        size += sys.getsizeof(getattr(self, manifest.keys))
        size += sys.getsizeof(getattr(self, manifest.values))
        return size

    @property
    def fingerprint(self) -> str:
        """Return a url-safe base64-encoded content hash of this manifest.

        Returns:
            str: A base64-encoded content hash.

        """
        return content_id(getattr(self, manifest.digest))

    @property
    def hexdigest(self) -> str:
        """Return a hexadecimal string of the content hash of this manifest.

        Returns:
            str: A hexadecimal string representation of the content hash.

        """
        return hex_id(getattr(self, manifest.digest))
