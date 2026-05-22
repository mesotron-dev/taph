"""The Manifest class module.

#TODO

"""

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

from taph.config.meta_conf import manifest_type_conf as manifest
from taph.exceptions import ManifestError
from taph.meta.manifest_meta import ManifestType
from taph.views.manifest_views import (
    ManifestItemsView,
    ManifestKeysView,
    ManifestValuesView,
)

__all__: tuple[str] = ('Manifest',)


class Manifest[Key: str, Value: object](metaclass=ManifestType):
    """Base class for static, non-instantiable constant containers.

    Attributes defined on a Manifest are frozen at class creation time.
    Attempting to instantiate a Manifest will raise an error.

    """

    __slots__ = ()

    __digest__: ClassVar[bytes]

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Manifest[str, object]:
        """Create a Manifest from a mapping (not implemented).

        This method exists for Mapping compatibility but is not supported for
        Manifest objects.

        Args:
            data (Mapping[str, object]): A mapping of field names to values.

        Raises:
            NotImplementedError: Always returns NotImplemented.

        """
        raise NotImplementedError(manifest.fromdict_not_implemented())

    @classmethod
    def fromkeys(cls, keys: Iterable[str], value: object = None) -> None:
        """Create a new Manifest from a sequence of keys (not implemented).

        This method exists for Mapping compatibility but is not supported for
        Manifest objects.

        Args:
            keys (Iterable[str]): A sequence of field names (not used).
            value (object, optional): A default value (not used).

        Raises:
            NotImplementedError: Always returns NotImplemented.

        """
        raise NotImplementedError(manifest.fromkeys_not_implemented())

    @classmethod
    def get(cls, key: object, default: object | None = None) -> object | None:
        """Return the key's value if key is in the Manifest, else default.

        Args:
            key (str): Field name to retrieve.
            default (object, optional): Value returned if key is not found
                or is the digest field. Defaults to None.

        Returns:
            object: Field value or default if not found.

        """
        try:
            keys: tuple[str, ...] = getattr(cls, manifest.keys, ())
            values: tuple[object, ...] = getattr(cls, manifest.values, ())
            return values[keys.index(key)]
        except ValueError:
            return default

    @classmethod
    def keys(cls) -> ManifestKeysView:
        """Return a view of the keys in a Manifest."""
        return ManifestKeysView(cls)

    @classmethod
    def values(cls) -> ManifestValuesView:
        """Return a view of the values in a Manifest."""
        return ManifestValuesView(cls)

    @classmethod
    def items(cls) -> ManifestItemsView:
        """Return a view of the items in a Manifest."""
        return ManifestItemsView(cls)

    @classmethod
    def copy(cls) -> type[Manifest[Key, Value]]:
        """Return the immutable cls."""
        return cls

    @classmethod
    def pop(cls, *args: object, **kwargs: object) -> None:  # noqa ARG003
        """Manifest modification is not permitted."""
        raise ManifestError(manifest.pop())

    @classmethod
    def popitem(cls) -> None:
        """Manifest modification is not permitted."""
        raise ManifestError(manifest.pop())

    @classmethod
    def clear(cls) -> None:
        """Manifest modification is not permitted."""
        raise ManifestError(manifest.clear())

    @classmethod
    def update(cls, *args: object, **kwargs: object) -> None:  # noqa #ARG003
        """Manifest modification is not permitted."""
        raise ManifestError(manifest.update())

    @classmethod
    def setdefault(cls, *args: object, **kwargs: object) -> None:  # noqa #ARG003
        """Manifest modification is not permitted."""
        raise ManifestError(manifest.setdefault())
