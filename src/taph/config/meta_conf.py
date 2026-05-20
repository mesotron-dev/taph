"""Configuration for the Taph metaclass modules."""

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterable


__all__: tuple[str, ...] = (
    'frozen_dict_conf',
    'manifest_type_conf',
    'record_type_conf',
    'taph_error_conf',
    'taph_type_conf',
)


class TaphTypeConf(NamedTuple):
    """Configuration for the taph_meta module."""

    abc: str = '_abc_'
    abc_methods: str = '__abstractmethods__'
    annotations: str = '__annotations__'
    del_attr: str = '___delattr__'
    set_attr: str = '__setattr__'
    init_attr: str = '__init__'
    slots: str = '__slots__'
    digest: str = '__digest__'
    qualname: str = '__qualname__'
    module: str = '__module__'
    # Generic exceptions
    parameters = '__parameters__'
    orig_bases = '__orig_bases__'
    mro_entries = '__mro_entries__'
    class_getitem = '__class_getitem__'
    is_protocol = '_is_protocol'
    init_subclass = '__init_subclass__'

    def class_internals(self) -> tuple[str, ...]:
        """Return class internals to exclude from freezing."""
        return (
            self.parameters,
            self.orig_bases,
            self.mro_entries,
            self.class_getitem,
            self.is_protocol,
            self.init_subclass
        )

taph_type_conf: TaphTypeConf = TaphTypeConf()


class TaphErrorConf(NamedTuple):
    """Configuration for TaphType error messages."""

    slots_err: str = (
        "must define '__slots__' to inherit from an Immutable type."
    )
    class_attr_err: str = 'attribute of an immutable class'
    from_keys_err: str = 'does not support the fromkeys class method.'
    instance_set_err: str = 'Cannot modify attribute'
    instance_del_err: str = 'Cannot delete attribute'
    immutable_instance: str = 'is immutable'

    def no_slots_message(self, name: str) -> str:
        """Default error message for an empty __slots__."""
        return f"Class '{name}' {self.slots_err}"

    def class_setattr(self, name: str) -> str:
        """Default class __setattr__ error message."""
        return f"Cannot modify '{self.class_attr_err}' '{name}'."

    def class_delattr(self, name: str) -> str:
        """Default class __delattr__ error message."""
        return f"Cannot delete '{self.class_attr_err}' '{name}'."

    def instance_setattr(self, instance: object, name: str) -> str:
        """Default instance __setattr__ error message."""
        return (
            f"{self.instance_set_err} '{name}'. "
            f"'{type(instance).__name__}' {self.immutable_instance}."
        )

    def instance_delattr(self, instance: object, name: str) -> str:
        """Default instance __delattr__ error message."""
        return (
            f"{self.instance_del_err} '{name}'. "
            f"'{type(instance).__name__}' {self.immutable_instance}."
        )


taph_error_conf: TaphErrorConf = TaphErrorConf()


class FrozenDictConf(NamedTuple):
    """#todo."""

    del_attr: str = taph_type_conf.del_attr
    set_attr: str = taph_type_conf.set_attr
    slots: str = taph_type_conf.slots
    index_attr: str = '_index_'
    keys: str = '_keys_'
    values: str = '_values_'
    digest: str = taph_type_conf.digest
    not_implemented: str = 'FrozenDict does not implement the fromkeys method.'

    def immutable(self, name: str) -> str:
        """Default pop/popitem error message."""
        return f'Cannot modify immutable {name}.'

    def subclass(self, name: str) -> str:
        """Default init_subclass error message."""
        return f"Cannot subclass immutable mapping '{name}'."


frozen_dict_conf: FrozenDictConf = FrozenDictConf()


class ManifestTypeConf(NamedTuple):
    """#todo."""

    del_attr: str = taph_type_conf.del_attr
    set_attr: str = taph_type_conf.set_attr
    slots: str = taph_type_conf.slots
    digest: str = taph_type_conf.digest
    keys: str = frozen_dict_conf.keys
    values: str = frozen_dict_conf.values
    immutable: str = 'A Manifest is an immutable class.'
    match_args: str = '__match_args__'
    not_implemented: str = 'Manifests do not implement'

    def clear(self) -> str:
        """Default clear error message."""
        return self.immutable

    def fromdict_not_implemented(self) -> str:
        """Default fromdict error message."""
        return f'{self.not_implemented} from_dict'

    def fromkeys_not_implemented(self) -> str:
        """Default fromkeys error message."""
        return f'{self.not_implemented} fromkeys'

    def pop(self) -> str:
        """Default pop error message."""
        return self.immutable

    def popitem(self) -> str:
        """Default popitem error message."""
        return self.immutable

    def setdefault(self) -> str:
        """Default setdefault error message."""
        return self.immutable

    def update(self) -> str:
        """Default update error message."""
        return self.immutable


manifest_type_conf: ManifestTypeConf = ManifestTypeConf()


class RecordTypeConf(NamedTuple):
    """Configuration for the record module."""

    annotations: str = taph_type_conf.annotations
    del_attr: str = taph_type_conf.del_attr
    set_attr: str = taph_type_conf.set_attr
    init: str = taph_type_conf.init_attr
    slots: str = taph_type_conf.slots
    digest: str = taph_type_conf.digest
    qualname: str = taph_type_conf.qualname
    module: str = taph_type_conf.module
    not_implemented: str = 'Record does not implement the fromkeys method.'

    def pop(self, item: object, name: object) -> str:
        """Return error message for a mapping pop."""
        return f'Cannot remove {item}.\n{self.record(name)}'

    def record(self, name: object) -> str:
        """Return error message for a record immutable error."""
        return f'{name!r} object is immutable.'

    def missing_fields(self, name: object, fields: Iterable[str]) -> str:
        """Return error messae for missing fields."""
        return (
            f'Cannot create {name}. Missing required fields: '
            f'{", ".join(fields)}'
        )

    def invalid_attribute_name(self, name: str, field: str) -> str:
        """Return message for invalid slot typeerror."""
        return f"Invalid attribute name '{field}' for Record '{name}'."

    def subclass_not_implemented(self) -> str:
        """Return __subclasshook__ error message."""
        return 'All subclasses of a Record are also Records.'

    def unannotated_var(self, key: str, value: object, name: str) -> str:
        """Return unannotated field error message."""
        return str(
            f"Invalid unannotated variable '{key}' in Record '{name}'. "
            f'Fields must be annotated (e.g. {key}: Any = {value!r}) '
            f'or declared as ClassVar.'
        )


record_type_conf: RecordTypeConf = RecordTypeConf()
