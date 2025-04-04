
from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.models import AiModel
from typing import Optional, Type, Any

@dataclass
class AiModelDTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))

class AiModelBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None, fetch_on_init_limit: int = 200, fetch_on_init_with_warnings_off: str = "YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100"):
        self.dto_class = dto_class or AiModelDTO
        super().__init__(AiModel, self.dto_class, fetch_on_init_limit, fetch_on_init_with_warnings_off)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model):
        pass

    async def create_ai_model(self, **data):
        return await self.create_item(**data)

    async def delete_ai_model(self, id):
        return await self.delete_item(id)

    async def get_ai_model_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_model_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_model(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_model(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_models(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_models(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_ai_models_by_name(self, name):
        return await self.load_items(name=name)

    async def filter_ai_models_by_name(self, name):
        return await self.filter_items(name=name)

    async def load_ai_models_by_common_name(self, common_name):
        return await self.load_items(common_name=common_name)

    async def filter_ai_models_by_common_name(self, common_name):
        return await self.filter_items(common_name=common_name)

    async def load_ai_models_by_provider(self, provider):
        return await self.load_items(provider=provider)

    async def filter_ai_models_by_provider(self, provider):
        return await self.filter_items(provider=provider)

    async def load_ai_models_by_endpoints(self, endpoints):
        return await self.load_items(endpoints=endpoints)

    async def filter_ai_models_by_endpoints(self, endpoints):
        return await self.filter_items(endpoints=endpoints)

    async def load_ai_models_by_model_class(self, model_class):
        return await self.load_items(model_class=model_class)

    async def filter_ai_models_by_model_class(self, model_class):
        return await self.filter_items(model_class=model_class)

    async def load_ai_models_by_model_provider(self, model_provider):
        return await self.load_items(model_provider=model_provider)

    async def filter_ai_models_by_model_provider(self, model_provider):
        return await self.filter_items(model_provider=model_provider)

    async def get_active_ai_models_with_ai_settings(self):
        return await self.get_active_items_with_one_relation('ai_settings')

    async def get_active_ai_model_with_ai_settings(self):
        return await self.get_active_item_with_one_relation('ai_settings')

    async def get_ai_model_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_models_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def get_active_ai_model_with_through_ai_settings(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'ai_settings', second_relationship)

    async def get_active_ai_models_with_ai_model_endpoints(self):
        return await self.get_active_items_with_one_relation('ai_model_endpoints')

    async def get_active_ai_model_with_ai_model_endpoints(self):
        return await self.get_active_item_with_one_relation('ai_model_endpoints')

    async def get_ai_model_with_ai_model_endpoints(self, id):
        return await self.get_item_with_related(id, 'ai_model_endpoints')

    async def get_ai_models_with_ai_model_endpoints(self):
        return await self.get_items_with_related('ai_model_endpoints')

    async def get_active_ai_model_with_through_ai_model_endpoints(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'ai_model_endpoints', second_relationship)

    async def get_active_ai_models_with_recipe_models(self):
        return await self.get_active_items_with_one_relation('recipe_models')

    async def get_active_ai_model_with_recipe_models(self):
        return await self.get_active_item_with_one_relation('recipe_models')

    async def get_ai_model_with_recipe_models(self, id):
        return await self.get_item_with_related(id, 'recipe_models')

    async def get_ai_models_with_recipe_models(self):
        return await self.get_items_with_related('recipe_models')

    async def get_active_ai_model_with_through_recipe_models(self, id, second_relationship):
        return await self.get_active_item_with_through_fk(id, 'recipe_models', second_relationship)

    async def load_ai_models_by_ids(self, ids):
        return await self.load_items_by_ids(ids)
    
    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)
    
    @property
    def active_ai_model_ids(self):
        return self.active_item_ids
