from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from common.utils.dynamic_field_handler import process_field_definitions, process_object_field_definitions, process_batch_field_definitions
from common.utils.fancy_prints import vcprint

import os

@dataclass
class BrokerObject:
    id: str
    default_value: Optional[str] = None
    ready: bool = False
    def to_dict(self):
        return {
            'id': self.id,
            'default_value': self.default_value,
            'ready': self.ready,
        }

FIELD_DEFINITIONS = {
    'id': {'type': 'str', 'always_include': True, 'default': None},
    'default_value': {'type': 'str', 'always_include': False, 'default': None},
    'ready': {'type': 'bool', 'always_include': True, 'default': False},
}

FIELD_MAP = {
    'broker_id': 'id',
    'broker_ready': 'ready',
}

def build_broker_object_from_kwargs(get_dict=False, **kwargs) -> BrokerObject:
    processed_data = process_field_definitions(FIELD_DEFINITIONS, **kwargs, convert_camel_case=True, fieldname_map=FIELD_MAP)
    obj = BrokerObject(**processed_data)
    if get_dict:
        return obj.to_dict()
    return obj

def build_broker_object_from_object(obj: Any, get_dict=False) -> BrokerObject:
    processed_data = process_object_field_definitions(FIELD_DEFINITIONS, obj, convert_camel_case=True, fieldname_map=FIELD_MAP)
    obj = BrokerObject(**processed_data)
    if get_dict:
        return obj.to_dict()
    return obj

def build_broker_object_from_batch_objects(objects: List[Any], get_dict=False) -> List[BrokerObject]:
    processed_data = process_batch_field_definitions(FIELD_DEFINITIONS, objects, convert_camel_case=True, fieldname_map=FIELD_MAP)
    objs = [BrokerObject(**data) for data in processed_data]
    if get_dict:
        return [obj.to_dict() for obj in objs]
    return objs


if __name__ == "__main__":
    os.system('cls')
    sample_data = {
        'id': 'This is a string',
        'default_value': 'This is a string',
        'ready': True,
    }
    vcprint(sample_data, "Full sample data", pretty=True, color="green")
    metadata_full = build_broker_object_from_kwargs(**sample_data)
    vcprint(metadata_full, "Resulting Metadata (full)", pretty=True, color="green")

    minimal_sample_data = {
        'id': 'This is a string',
    }

    vcprint(minimal_sample_data, "Minimal sample data (required fields only)", pretty=True, color="yellow")
    metadata_minimal = build_broker_object_from_kwargs(**minimal_sample_data)
    vcprint(metadata_minimal, "Resulting Metadata (minimal)", pretty=True, color="yellow")

    metadata_from_object = build_broker_object_from_object(metadata_full)
    vcprint(metadata_from_object, "Resulting Metadata (from object)", pretty=True, color="blue")

    metadata_from_batch_objects = build_broker_object_from_batch_objects([metadata_full, metadata_minimal])
    vcprint(metadata_from_batch_objects, "Resulting Metadata (from batch objects)", pretty=True, color="purple")