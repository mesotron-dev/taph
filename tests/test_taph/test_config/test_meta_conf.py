"""Tests for the taph.config.meta_conf module."""
from taph.config.meta_conf import (
    frozen_dict_conf,
    manifest_type_conf,
    record_type_conf,
    taph_error_conf,
    taph_type_conf,
)


class DummyInstance:
    """Mock object class to pass validation context checks."""

    __slots__ = ()


def test_taph_type_constants_and_internals() -> None:
    """Verify system-level metadata string configurations and internal filtering."""
    assert taph_type_conf.abc == '_abc_'
    assert taph_type_conf.slots == '__slots__'
    assert taph_type_conf.digest == '__digest__'

    internals = taph_type_conf.class_internals()
    assert taph_type_conf.parameters in internals
    assert taph_type_conf.orig_bases in internals
    assert taph_type_conf.mro_entries in internals
    assert taph_type_conf.class_getitem in internals
    assert taph_type_conf.is_protocol in internals
    assert taph_type_conf.init_subclass in internals
    assert len(internals) == 6


def test_taph_error_message_formatting_exact() -> None:
    """Verify exact output string match constraints for Taph error messages."""
    # 1. Class level checks
    assert (
        taph_error_conf.no_slots_message('Mock')
        == "Class 'Mock' must define '__slots__' to inherit from an Immutable type."
    )
    assert (
        taph_error_conf.class_setattr('X')
        == "Cannot modify 'attribute of an immutable class' 'X'."
    )
    assert (
        taph_error_conf.class_delattr('Y')
        == "Cannot delete 'attribute of an immutable class' 'Y'."
    )

    # 2. Instance level checks
    instance = DummyInstance()
    assert (
        taph_error_conf.instance_setattr(instance, 'field_x')
        == "Cannot modify attribute 'field_x'. 'DummyInstance' is immutable."
    )
    assert (
        taph_error_conf.instance_delattr(instance, 'field_y')
        == "Cannot delete attribute 'field_y'. 'DummyInstance' is immutable."
    )


def test_frozen_dict_config_paths() -> None:
    """Verify FrozenDict exception policy and mapping validation rules."""
    assert (
        frozen_dict_conf.immutable('CustomDict')
        == 'Cannot modify immutable CustomDict.'
    )
    assert (
        frozen_dict_conf.not_implemented
        == 'FrozenDict does not implement the fromkeys method.'
    )
    assert (
        frozen_dict_conf.subclass('FinalDict')
        == "Cannot subclass immutable mapping 'FinalDict'."
    )
    assert frozen_dict_conf.index_attr == '_index_'


def test_manifest_type_config_paths() -> None:
    """Verify Manifest specific error messages and constant definitions."""
    assert manifest_type_conf.clear() == 'A Manifest is an immutable class.'
    assert (
        manifest_type_conf.fromdict_not_implemented()
        == 'Manifests do not implement from_dict'
    )
    assert (
        manifest_type_conf.fromkeys_not_implemented()
        == 'Manifests do not implement fromkeys'
    )
    assert manifest_type_conf.pop() == 'A Manifest is an immutable class.'
    assert manifest_type_conf.popitem() == 'A Manifest is an immutable class.'
    assert (
        manifest_type_conf.setdefault() == 'A Manifest is an immutable class.'
    )
    assert manifest_type_conf.update() == 'A Manifest is an immutable class.'
    assert manifest_type_conf.match_args == '__match_args__'


def test_record_type_config_paths_exact() -> None:
    """Verify Record schema layout messaging matches exact template designs."""
    assert (
        record_type_conf.pop('secret_key', 'UserRecord')
        == "Cannot remove secret_key.\n'UserRecord' object is immutable."
    )
    assert (
        record_type_conf.not_implemented
        == 'Record does not implement the fromkeys method.'
    )
    assert (
        record_type_conf.invalid_attribute_name('Data', '123_bad')
        == "Invalid attribute name '123_bad' for Record 'Data'."
    )
    assert (
        record_type_conf.subclass_not_implemented()
        == 'All subclasses of a Record are also Records.'
    )
    assert (
        record_type_conf.unannotated_var('count', 0, 'Counter')
        == "Invalid unannotated variable 'count' in Record 'Counter'. "
        "Fields must be annotated (e.g. count: Any = 0) or declared as ClassVar."
    )


def test_record_missing_fields_boundaries() -> None:
    """MC/DC: Test boundary conditions of the list-joining logic in missing_fields."""
    # Boundary 1: Empty iterable (0 elements)
    assert (
        record_type_conf.missing_fields('Profile', [])
        == 'Cannot create Profile. Missing required fields: '
    )

    # Boundary 2: Single element (1 element - no joining comma)
    assert (
        record_type_conf.missing_fields('Profile', ['uuid'])
        == 'Cannot create Profile. Missing required fields: uuid'
    )

    # Boundary 3: Multiple elements (N elements - structured comma joining)
    assert (
        record_type_conf.missing_fields('Profile', ['uuid', 'token', 'email'])
        == 'Cannot create Profile. Missing required fields: uuid, token, email'
    )
