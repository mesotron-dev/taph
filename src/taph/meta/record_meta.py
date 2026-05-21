"""The RecordType class module."""
import textwrap
from annotationlib import (
    Format,
    call_annotate_function,
    get_annotate_from_class_namespace,
)
from typing import cast

from taph.config.meta_conf import record_type_conf as record
from taph.meta.taph_meta import TaphType
from taph.tools.core_tools import is_classvar, namespace_skip
from taph.tools.freeze_tools import freeze
from taph.tools.hash_tools import mk_digest
from taph.tools.validation_tools import is_valid_slot

__all__: tuple[str] = ('RecordType',)


def _compile_init(
    name: str, fields: list[str], defaults: dict[str, object]
) -> object:
    """Compile the Record constructor.

    Ensures all arguments are frozen at the boundary, assigned to slots, and
    accurately hashed to form the permanent content digest.

    """
    args: list[str] = ['self']
    exec_globals = {'freeze': freeze, 'mk_digest': mk_digest, 'object': object}

    for f in fields:
        if f in defaults:
            exec_globals[f'_def_{f}'] = defaults.get(f)
            args.append(f'{f}=_def_{f}')
        else:
            args.append(f)

    body: list[str] = []
    for f in fields:
        body.append(f'frozen_{f} = freeze({f})')
        body.append(f'object.__setattr__(self, {f!r}, frozen_{f})')

    items = [f'({f!r}, frozen_{f})' for f in fields]
    items_csv = ', '.join(items)
    if len(fields) == 1:
        items_csv += ','

    content_digest = f'({name!r}, {items_csv})'
    body.append(
        f'object.__setattr__(self, "__digest__", mk_digest({content_digest}))'
    )

    source = f'def __init__({", ".join(args)}):\n'
    if body:
        source += textwrap.indent('\n'.join(body), '    ')
    else:
        source += '    pass\n'

    locals_dict: dict[str, object] = {}
    exec(source, exec_globals, locals_dict) # noqa: S102

    return locals_dict.get('__init__')


def _namespace_guard(
    name: str, annotations: dict[str, object], namespace: dict[str, object]
) -> None:
    """Enforce the strict Record typing contract.

    Validates that all public, non-callable attributes in the class namespace
    are strictly annotated.

    Raises:
        TypeError: If an unannotated state attribute is detected.

    """
    for key, value in namespace.items():
        if namespace_skip(value, key=key):
            continue

        if key not in annotations and key not in (
            record.slots,
            record.qualname,
            record.module,
        ):
            raise TypeError(record.unannotated_var(key, value, name))


def _prepare_record_fields(
    name: str, annotations: dict[str, object], namespace: dict[str, object]
) -> tuple[list[str], dict[str, object]]:
    """Parse annotations to collect valid fields and securely freeze defaults.

    Args:
        name: The name of the class being created.
        annotations: The __annotations__ dictionary of the class.
        namespace: The class namespace dictionary containing.

    Returns:
        A tuple containing:
        1. A list of valid, non-ClassVar field names.
        2. A dictionary mapping field names to their frozen default values.

    Raises:
        TypeError: If an field name is not a valid Python identifier or slot.

    """
    current_fields: list[str] = []
    default_fields: dict[str, object] = {}

    for field, hint in annotations.items():
        if is_classvar(hint):
            continue

        if field in (record.slots, record.digest):
            continue

        if not is_valid_slot(field):
            raise TypeError(record.invalid_attribute_name(name, field))

        current_fields.append(field)

        if field in namespace:
            default_fields[field] = freeze(namespace[field])

    return current_fields, default_fields


def _check_mro_fields(
    mcls: type,
    bases: tuple[type, ...],
    fields: list[str],
    annotations: dict[str, object],
) -> tuple[list[str], dict[str, object]]:
    """Check the MRO to inherit base fields and merge annotations.

    Ensure that inherited fields preced the subclass & maintain structural
    compatibility in the constructor signature. And merge the type annotations
    while allowing preference for subclass overrides.

    Args:
        mcls: The metaclass (RecordType) used to identify valid base classes.
        bases: The base classes of the new class.
        fields: The fields explicitly defined on the new subclass.
        annotations: The annotations defined on the new subclass.

    Returns:
        A tuple containing:
        1. A list of all ordered fields (inherited + current).
        2. A dictionary of the finalized, merged annotations.

    """
    record_fields: list[str] = []
    record_annotations: dict[str, object] = {}
    current_annotations: dict[str, object] = dict(annotations)

    for base in reversed(bases):
        if isinstance(base, mcls):
            base_slots = getattr(base, record.slots, ())[:-1]
            for f in base_slots:
                if f not in record_fields:
                    record_fields.append(f)

            base_notes = getattr(base, record.annotations, {})
            record_annotations = {**base_notes, **current_annotations}

    for f in fields:
        if f not in record_fields:
            record_fields.append(f)

    return record_fields, record_annotations


def _get_annotations(namespace: dict[str, object]) -> dict[str, object]:
    """Extract type annotations from a class namespace dict."""
    try:
        ann_func = get_annotate_from_class_namespace(namespace)
        if ann_func is not None:
            return call_annotate_function(ann_func, format=Format.VALUE)
    except ImportError:
        pass
    return cast(
        'dict[str, object]', namespace.get(record.annotations, {})
    )

class RecordType(TaphType):
    """Metaclass for immutable instance container for Records."""

    __slots__ = ()

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
    ) -> type:
        """Compile a new Record class."""
        # Look forward for annotations
        annotations: dict[str, object] = _get_annotations(namespace)

        # Typed Attribute Guard
        _namespace_guard(name, annotations, namespace)

        # Get valid fields and frozen defaults
        fields, default_fields = _prepare_record_fields(
            name, annotations, namespace
        )

        # Resolve Inheritance
        record_fields, record_annotations = _check_mro_fields(
            cls, bases, fields, annotations
        )
        # Prepare __slots__
        record_slots: tuple[str, ...] = (*record_fields, record.digest)

        # Create the constructor
        init: object = _compile_init(name, record_fields, default_fields)

        # Prepare Record namespace
        namespace['__init__'] = init
        namespace[record.annotations] = record_annotations
        namespace[record.slots] = record_slots

        # Cleanup class namespace
        for field in record_fields:
            namespace.pop(field, None)

        # Seal instance immutability
        namespace[record.set_attr] = TaphType._block_setattr
        namespace[record.del_attr] = TaphType._block_delattr

        # Create the class
        new_class = super().__new__(cls, name, bases, namespace)

        # Force it again after class creation
        type.__setattr__(new_class, '__init__', init)

        return new_class
