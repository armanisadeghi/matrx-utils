from database.orm.models import DataBroker
from database.orm.core.relations import (
    ForeignKey,
    ForeignKeyReference,
    InverseForeignKeyReference,
)


def print_section(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def inspect_field_creation():
    print_section("Field Creation Test")

    # Create test fields
    fk = ForeignKey(is_native=True, to_model="TestModel")
    fk_ref = ForeignKeyReference(
        field_name="test_field",
        to_model="TestModel",
        related_name="test",
        is_native=False,
    )
    inv_fk = InverseForeignKeyReference(from_model="TestModel", from_field="test_id", related_name="id")

    print("ForeignKey type:", type(fk))
    print("ForeignKey bases:", ForeignKey.__bases__)
    print("ForeignKey dict:", fk.__dict__)

    print("\nForeignKeyReference type:", type(fk_ref))
    print("ForeignKeyReference bases:", ForeignKeyReference.__bases__)
    print("ForeignKeyReference dict:", fk_ref.__dict__)

    print("\nInverseForeignKeyReference type:", type(inv_fk))
    print("InverseForeignKeyReference bases:", InverseForeignKeyReference.__bases__)
    print("InverseForeignKeyReference dict:", inv_fk.__dict__)


def inspect_metaclass_processing():
    print_section("Metaclass Processing")

    # Look at how ModelMeta processes fields
    print("Model _meta fields:", DataBroker._meta.fields.keys())
    print("\nField types in _meta:")
    for name, field in DataBroker._meta.fields.items():
        print(f"  {name}: {type(field)}")
        print(f"    dict: {field.__dict__}")

    print("\nModel _fields:", DataBroker._fields.keys())
    print("\nField types in _fields:")
    for name, field in DataBroker._fields.items():
        print(f"  {name}: {type(field)}")
        print(f"    dict: {field.__dict__}")


def inspect_relationship_lookup():
    print_section("Relationship Lookup Methods")

    # Test get_field and get_relation methods
    test_fields = [
        "default_component",
        "data_input_component_reference",
        "message_brokers_inverse",
    ]

    print("Direct field access:")
    for field_name in test_fields:
        print(f"\nField: {field_name}")
        if hasattr(DataBroker, field_name):
            field = getattr(DataBroker, field_name)
            print("  Type:", type(field))
            print("  Dict:", field.__dict__)

    print("\nget_field() access:")
    for field_name in test_fields:
        print(f"\nField: {field_name}")
        field = DataBroker.get_field(field_name)
        if field:
            print("  Type:", type(field))
            print("  Dict:", field.__dict__)


def inspect_meta_relationships():
    print_section("Meta Relationship Information")

    meta = DataBroker._meta
    print("Foreign Keys in _meta:", meta.foreign_keys)
    print("\nForeign Key types:")
    for name, fk in meta.foreign_keys.items():
        print(f"  {name}: {type(fk)}")
        print(f"    dict: {fk.__dict__}")

    print("\nInverse Foreign Keys in _meta:", meta.inverse_foreign_keys)
    print("\nInverse FK types:")
    for name, ifk in meta.inverse_foreign_keys.items():
        print(f"  {name}: {type(ifk)}")
        print(f"    dict: {ifk.__dict__}")


if __name__ == "__main__":
    inspect_field_creation()
    inspect_metaclass_processing()
    inspect_relationship_lookup()
    inspect_meta_relationships()
