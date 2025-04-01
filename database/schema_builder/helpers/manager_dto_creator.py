import os
from common import plt

def generate_base_manager_class(model_pascal: str, model_name: str, model_name_plural: str) -> str:
    """Generate the minimal core manager class without optional method sets."""
    return f"""
from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.models import {model_pascal}
from typing import Optional, Type, Any

@dataclass
class {model_pascal}DTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))

class {model_pascal}Base(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or {model_pascal}DTO
        super().__init__({model_pascal}, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, {model_name.lower()}):
        pass

    async def create_{model_name}(self, **data):
        return await self.create_item(**data)

    async def delete_{model_name}(self, id):
        return await self.delete_item(id)

    async def get_{model_name}_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_{model_name}_by_id(self, id):
        return await self.load_by_id(id)

    async def load_{model_name}(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_{model_name}(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_{model_name_plural}(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_{model_name_plural}(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)
"""

def generate_to_dict_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods that return dict versions of data."""
    return f"""
    async def create_{model_name}_get_dict(self, **data):
        return await self.create_item_get_dict(**data)

    async def filter_{model_name_plural}_get_dict(self, **kwargs):
        return await self.filter_items_get_dict(**kwargs)

    async def get_active_{model_name}_dict(self, id):
        return await self.get_active_item_dict(id)

    async def get_active_{model_name_plural}_dict(self):
        return await self.get_active_items_dict()

    async def get_active_{model_name_plural}_with_all_related_dict(self):
        return await self.get_active_items_with_all_related_dict()

    async def get_active_{model_name_plural}_with_ifks_dict(self):
        return await self.get_active_items_with_ifks_dict()

    async def get_{model_name}_dict(self, id):
        return await self.get_item_dict(id)

    async def get_{model_name_plural}_dict(self, **kwargs):
        return await self.get_items_dict(**kwargs)

    async def get_{model_name_plural}_with_all_related_dict(self):
        return await self.get_items_with_all_related_dict()

    async def load_{model_name}_get_dict(self, use_cache=True, **kwargs):
        return await self.load_item_get_dict(use_cache, **kwargs)

    async def load_{model_name_plural}_by_ids_get_dict(self, ids):
        return await self.load_items_by_ids_get_dict(ids)

    async def update_{model_name}_get_dict(self, id, **updates):
        return await self.update_item_get_dict(id, **updates)
"""

def generate_active_methods(model_name: str, model_name_plural: str) -> str:
    """Generate methods related to handling active items."""
    return f"""
    async def add_active_{model_name}_by_id(self, id):
        return await self.add_active_by_id(id)

    async def add_active_{model_name}_by_ids(self, ids):
        return await self.add_active_by_ids(ids)

    async def get_active_{model_name}(self, id):
        return await self.get_active_item(id)

    async def get_active_{model_name_plural}(self):
        return await self.get_active_items()

    async def get_active_{model_name_plural}_with_all_related(self):
        return await self.get_active_items_with_all_related()

    async def get_active_{model_name_plural}_with_fks(self):
        return await self.get_active_items_with_fks()

    async def get_active_{model_name_plural}_with_ifks(self):
        return await self.get_active_items_with_ifks()

    async def get_active_{model_name_plural}_with_related_models_list(self, related_models_list):
        return await self.get_active_items_with_related_models_list(related_models_list)

    async def get_active_{model_name}_through_ifk(self, id, first_relationship, second_relationship):
        return await self.get_active_item_through_ifk(id, first_relationship, second_relationship)

    async def get_active_{model_name}_with_all_related(self):
        return await self.get_active_item_with_all_related()

    async def get_active_{model_name}_with_fk(self, id, related_model):
        return await self.get_active_item_with_fk(id, related_model)

    async def get_active_{model_name}_with_ifk(self, related_model):
        return await self.get_active_item_with_ifk(related_model)

    async def get_active_{model_name}_with_related_models_list(self, related_models_list):
        return await self.get_active_item_with_related_models_list(related_models_list)

    async def get_active_{model_name}_with_through_fk(self, id, first_relationship, second_relationship):
        return await self.get_active_item_with_through_fk(id, first_relationship, second_relationship)

    async def remove_active_{model_name}_by_id(self, id):
        await self.remove_active_by_id(id)

    async def remove_active_{model_name}_by_ids(self, ids):
        await self.remove_active_by_ids(ids)

    async def remove_all_active(self):
        await self.remove_all_active()
"""

def generate_or_not_methods(model_name: str, model_name_plural: str) -> str:
    """Generate 'or_not' methods that optionally handle items."""
    return f"""
    async def add_active_{model_name}_by_id_or_not(self, id=None):
        return await self.add_active_by_id_or_not(id)

    async def add_active_{model_name}_by_ids_or_not(self, ids=None):
        return await self.add_active_by_ids_or_not(ids)

    async def add_active_{model_name}_by_item_or_not(self, {model_name}=None):
        return await self.add_active_by_item_or_not({model_name})

    async def add_active_{model_name}_by_items_or_not(self, {model_name_plural}=None):
        return await self.add_active_by_items_or_not({model_name_plural})
"""

def generate_relation_methods(model_name: str, model_name_plural: str, relations: list[str]) -> str:
    """Generate methods specific to each relation."""
    return ''.join([
        f'''
    async def get_active_{model_name_plural}_with_{relation}(self):
        return await self.get_active_items_with_one_relation('{relation}')

    async def get_active_{model_name}_with_{relation}(self):
        return await self.get_active_item_with_one_relation('{relation}')

    async def get_{model_name}_with_{relation}(self, id):
        return await self.get_item_with_related(id, '{relation}')

    async def get_{model_name_plural}_with_{relation}(self):
        return await self.get_items_with_related('{relation}')

    async def get_active_{model_name}_with_through_{relation}(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, '{relation}', second_relationship)
'''
        for relation in relations
    ])

def generate_to_dict_relation_methods(model_name: str, model_name_plural: str, relations: list[str]) -> str:
    """Generate to_dict methods specific to each relation."""
    return ''.join([
        f'''
    async def get_active_{model_name}_with_{relation}_dict(self):
        return await self.get_active_item_with_one_relation_dict('{relation}')

    async def get_{model_name_plural}_with_{relation}_dict(self):
        return await self.get_items_with_related_dict('{relation}')
'''
        for relation in relations
    ])

def generate_filter_field_methods(model_name: str, model_name_plural: str, filter_fields: list[str]) -> str:
    """Generate filter-specific methods for each field in filter_fields."""
    return ''.join([
        f'''
    async def load_{model_name_plural}_by_{field}(self, {field}):
        return await self.load_items({field}={field})

    async def filter_{model_name_plural}_by_{field}(self, {field}):
        return await self.filter_items({field}={field})
'''
        for field in filter_fields
    ])

def generate_manager_class(
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    relations: list[str],
    filter_fields: list[str],
    include_to_dict: bool = False,
    include_active_methods: bool = False
) -> str:
    """Combine all parts into the full class, conditionally including optional methods."""
    base = generate_base_manager_class(model_pascal, model_name, model_name_plural)
    
    parts = [base]
    
    if include_active_methods:
        parts.append(generate_active_methods(model_name, model_name_plural))
        parts.append(generate_or_not_methods(model_name, model_name_plural))
    
    parts.append(generate_filter_field_methods(model_name, model_name_plural, filter_fields))
    parts.append(generate_relation_methods(model_name, model_name_plural, relations))
    
    if include_to_dict:
        parts.append(generate_to_dict_methods(model_name, model_name_plural))
        parts.append(generate_to_dict_relation_methods(model_name, model_name_plural, relations))
    
    parts.append(f"""
    async def load_{model_name_plural}_by_ids(self, ids):
        return await self.load_items_by_ids(ids)
    
    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)
    
    @property
    def active_{model_name}_ids(self):
        return self.active_item_ids
""")
    
    return ''.join(parts)

def save_manager_class(
    model_pascal: str,
    model_name: str,
    model_name_plural: str,
    relations: list[str],
    filter_fields: list[str],
    include_to_dict: bool = False,
    include_active_methods: bool = False
) -> tuple[str, str]:
    file_path = os.path.join("database", "orm", "extended", "managers", f"{model_name}_base.py")
    
    # Create the directory structure if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    model_class_str = generate_manager_class(
        model_pascal,
        model_name,
        model_name_plural,
        relations,
        filter_fields,
        include_to_dict,
        include_active_methods
    )

    # Always write (or overwrite) the file
    with open(file_path, "w") as f:
        f.write(model_class_str)
    
    plt(file_path, "Manager class saved")
    return model_class_str, file_path


if __name__ == "__main__":
    os.system("cls")
    
    model_pascal = "AiEndpoint"
    model_name = "ai_endpoint"
    model_name_plural = "ai_endpoints"
    filter_fields = ["name", "provider"]
    relations = ["ai_settings", "ai_model_endpoints", "recipe_models"]

    # Example with both to_dict and active methods included
    model_class_str, file_path = save_manager_class(
        model_pascal,
        model_name,
        model_name_plural,
        relations,
        filter_fields,
        include_to_dict=False,
        include_active_methods=False
    )

    # Example with only filter fields and relations, no to_dict or active methods
    # model_class_str, file_path = save_manager_class(
    #     model_pascal,
    #     model_name,
    #     model_name_plural,
    #     relations,
    #     filter_fields,
    #     include_to_dict=False,
    #     include_active_methods=False
    # )