# File: database/orm/extended/managers/all_managers.py

from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Recipe
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_item.id)
        await self._process_core_data(recipe_item)
        await self._process_metadata(recipe_item)
        await self._initial_validation(recipe_item)
        self.initialized = True

    async def _process_core_data(self, recipe_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeDTO
        super().__init__(Recipe, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe):
        pass

    async def create_recipe(self, **data):
        return await self.create_item(**data)

    async def delete_recipe(self, id):
        return await self.delete_item(id)

    async def get_recipe_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipes(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipes(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_with_compiled_recipe(self, id):
        return await self.get_item_with_related(id, 'compiled_recipe')

    async def get_recipes_with_compiled_recipe(self):
        return await self.get_items_with_related('compiled_recipe')

    async def get_recipe_with_ai_agent(self, id):
        return await self.get_item_with_related(id, 'ai_agent')

    async def get_recipes_with_ai_agent(self):
        return await self.get_items_with_related('ai_agent')

    async def get_recipe_with_recipe_display(self, id):
        return await self.get_item_with_related(id, 'recipe_display')

    async def get_recipes_with_recipe_display(self):
        return await self.get_items_with_related('recipe_display')

    async def get_recipe_with_recipe_processor(self, id):
        return await self.get_item_with_related(id, 'recipe_processor')

    async def get_recipes_with_recipe_processor(self):
        return await self.get_items_with_related('recipe_processor')

    async def get_recipe_with_recipe_model(self, id):
        return await self.get_item_with_related(id, 'recipe_model')

    async def get_recipes_with_recipe_model(self):
        return await self.get_items_with_related('recipe_model')

    async def get_recipe_with_recipe_broker(self, id):
        return await self.get_item_with_related(id, 'recipe_broker')

    async def get_recipes_with_recipe_broker(self):
        return await self.get_items_with_related('recipe_broker')

    async def get_recipe_with_recipe_message(self, id):
        return await self.get_item_with_related(id, 'recipe_message')

    async def get_recipes_with_recipe_message(self):
        return await self.get_items_with_related('recipe_message')

    async def get_recipe_with_recipe_tool(self, id):
        return await self.get_item_with_related(id, 'recipe_tool')

    async def get_recipes_with_recipe_tool(self):
        return await self.get_items_with_related('recipe_tool')

    async def get_recipe_with_recipe_function(self, id):
        return await self.get_item_with_related(id, 'recipe_function')

    async def get_recipes_with_recipe_function(self):
        return await self.get_items_with_related('recipe_function')

    async def load_recipes_by_status(self, status):
        return await self.load_items(status=status)

    async def filter_recipes_by_status(self, status):
        return await self.filter_items(status=status)

    async def load_recipes_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_recipes_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_recipes_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_ids(self):
        return self.active_item_ids



class RecipeManager(RecipeBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_manager_instance = RecipeManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomain
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_item.id)
        await self._process_core_data(scrape_domain_item)
        await self._process_metadata(scrape_domain_item)
        await self._initial_validation(scrape_domain_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainDTO
        super().__init__(ScrapeDomain, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain):
        pass

    async def create_scrape_domain(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domains(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domains(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_with_scrape_path_pattern(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern')

    async def get_scrape_domains_with_scrape_path_pattern(self):
        return await self.get_items_with_related('scrape_path_pattern')

    async def get_scrape_domain_with_scrape_job(self, id):
        return await self.get_item_with_related(id, 'scrape_job')

    async def get_scrape_domains_with_scrape_job(self):
        return await self.get_items_with_related('scrape_job')

    async def get_scrape_domain_with_scrape_domain_quick_scrape_settings(self, id):
        return await self.get_item_with_related(id, 'scrape_domain_quick_scrape_settings')

    async def get_scrape_domains_with_scrape_domain_quick_scrape_settings(self):
        return await self.get_items_with_related('scrape_domain_quick_scrape_settings')

    async def get_scrape_domain_with_scrape_domain_disallowed_notes(self, id):
        return await self.get_item_with_related(id, 'scrape_domain_disallowed_notes')

    async def get_scrape_domains_with_scrape_domain_disallowed_notes(self):
        return await self.get_items_with_related('scrape_domain_disallowed_notes')

    async def get_scrape_domain_with_scrape_domain_robots_txt(self, id):
        return await self.get_item_with_related(id, 'scrape_domain_robots_txt')

    async def get_scrape_domains_with_scrape_domain_robots_txt(self):
        return await self.get_items_with_related('scrape_domain_robots_txt')

    async def get_scrape_domain_with_scrape_domain_notes(self, id):
        return await self.get_item_with_related(id, 'scrape_domain_notes')

    async def get_scrape_domains_with_scrape_domain_notes(self):
        return await self.get_items_with_related('scrape_domain_notes')

    async def get_scrape_domain_with_scrape_domain_sitemap(self, id):
        return await self.get_item_with_related(id, 'scrape_domain_sitemap')

    async def get_scrape_domains_with_scrape_domain_sitemap(self):
        return await self.get_items_with_related('scrape_domain_sitemap')

    async def get_scrape_domain_with_scrape_task(self, id):
        return await self.get_item_with_related(id, 'scrape_task')

    async def get_scrape_domains_with_scrape_task(self):
        return await self.get_items_with_related('scrape_task')

    async def get_scrape_domain_with_scrape_quick_failure_log(self, id):
        return await self.get_item_with_related(id, 'scrape_quick_failure_log')

    async def get_scrape_domains_with_scrape_quick_failure_log(self):
        return await self.get_items_with_related('scrape_quick_failure_log')

    async def load_scrape_domains_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_ids(self):
        return self.active_item_ids



class ScrapeDomainManager(ScrapeDomainBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_manager_instance = ScrapeDomainManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeJob
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeJobDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_job_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_job_item.id)
        await self._process_core_data(scrape_job_item)
        await self._process_metadata(scrape_job_item)
        await self._initial_validation(scrape_job_item)
        self.initialized = True

    async def _process_core_data(self, scrape_job_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_job_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_job_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeJobDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeJobBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeJobDTO
        super().__init__(ScrapeJob, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_job):
        pass

    async def create_scrape_job(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_job(self, id):
        return await self.delete_item(id)

    async def get_scrape_job_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_job_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_job(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_job(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_jobs(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_jobs(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_job_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_jobs_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def get_scrape_job_with_scrape_cycle_tracker(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_tracker')

    async def get_scrape_jobs_with_scrape_cycle_tracker(self):
        return await self.get_items_with_related('scrape_cycle_tracker')

    async def get_scrape_job_with_scrape_task(self, id):
        return await self.get_item_with_related(id, 'scrape_task')

    async def get_scrape_jobs_with_scrape_task(self):
        return await self.get_items_with_related('scrape_task')

    async def load_scrape_jobs_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_jobs_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_jobs_by_start_urls(self, start_urls):
        return await self.load_items(start_urls=start_urls)

    async def filter_scrape_jobs_by_start_urls(self, start_urls):
        return await self.filter_items(start_urls=start_urls)

    async def load_scrape_jobs_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_jobs_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_jobs_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_job_ids(self):
        return self.active_item_ids



class ScrapeJobManager(ScrapeJobBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeJobManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_job_manager_instance = ScrapeJobManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiProvider
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiProviderDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_provider_item):
        '''Override the base initialization method.'''
        self.id = str(ai_provider_item.id)
        await self._process_core_data(ai_provider_item)
        await self._process_metadata(ai_provider_item)
        await self._initial_validation(ai_provider_item)
        self.initialized = True

    async def _process_core_data(self, ai_provider_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_provider_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_provider_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiProviderDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiProviderBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiProviderDTO
        super().__init__(AiProvider, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_provider):
        pass

    async def create_ai_provider(self, **data):
        return await self.create_item(**data)

    async def delete_ai_provider(self, id):
        return await self.delete_item(id)

    async def get_ai_provider_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_provider_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_provider(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_provider(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_providers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_providers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_provider_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_providers_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def get_ai_provider_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_ai_providers_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def load_ai_providers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_provider_ids(self):
        return self.active_item_ids



class AiProviderManager(AiProviderBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiProviderManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_provider_manager_instance = AiProviderManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import DataInputComponent
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class DataInputComponentDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, data_input_component_item):
        '''Override the base initialization method.'''
        self.id = str(data_input_component_item.id)
        await self._process_core_data(data_input_component_item)
        await self._process_metadata(data_input_component_item)
        await self._initial_validation(data_input_component_item)
        self.initialized = True

    async def _process_core_data(self, data_input_component_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, data_input_component_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, data_input_component_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[DataInputComponentDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class DataInputComponentBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or DataInputComponentDTO
        super().__init__(DataInputComponent, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_input_component):
        pass

    async def create_data_input_component(self, **data):
        return await self.create_item(**data)

    async def delete_data_input_component(self, id):
        return await self.delete_item(id)

    async def get_data_input_component_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_data_input_component_by_id(self, id):
        return await self.load_by_id(id)

    async def load_data_input_component(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_data_input_component(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_data_input_components(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_data_input_components(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_data_input_component_with_message_broker(self, id):
        return await self.get_item_with_related(id, 'message_broker')

    async def get_data_input_components_with_message_broker(self):
        return await self.get_items_with_related('message_broker')

    async def get_data_input_component_with_broker(self, id):
        return await self.get_item_with_related(id, 'broker')

    async def get_data_input_components_with_broker(self):
        return await self.get_items_with_related('broker')

    async def get_data_input_component_with_data_broker(self, id):
        return await self.get_item_with_related(id, 'data_broker')

    async def get_data_input_components_with_data_broker(self):
        return await self.get_items_with_related('data_broker')

    async def load_data_input_components_by_options(self, options):
        return await self.load_items(options=options)

    async def filter_data_input_components_by_options(self, options):
        return await self.filter_items(options=options)

    async def load_data_input_components_by_component(self, component):
        return await self.load_items(component=component)

    async def filter_data_input_components_by_component(self, component):
        return await self.filter_items(component=component)

    async def load_data_input_components_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_data_input_component_ids(self):
        return self.active_item_ids



class DataInputComponentManager(DataInputComponentBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataInputComponentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

data_input_component_manager_instance = DataInputComponentManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeCachePolicy
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeCachePolicyDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_cache_policy_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_cache_policy_item.id)
        await self._process_core_data(scrape_cache_policy_item)
        await self._process_metadata(scrape_cache_policy_item)
        await self._initial_validation(scrape_cache_policy_item)
        self.initialized = True

    async def _process_core_data(self, scrape_cache_policy_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_cache_policy_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_cache_policy_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeCachePolicyDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeCachePolicyBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeCachePolicyDTO
        super().__init__(ScrapeCachePolicy, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cache_policy):
        pass

    async def create_scrape_cache_policy(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_cache_policy(self, id):
        return await self.delete_item(id)

    async def get_scrape_cache_policy_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_cache_policy_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_cache_policy(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_cache_policy(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_cache_policies(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_cache_policies(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_cache_policy_with_scrape_path_pattern_cache_policy(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_cache_policy')

    async def get_scrape_cache_policies_with_scrape_path_pattern_cache_policy(self):
        return await self.get_items_with_related('scrape_path_pattern_cache_policy')

    async def load_scrape_cache_policies_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_cache_policies_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_cache_policies_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_cache_policy_ids(self):
        return self.active_item_ids



class ScrapeCachePolicyManager(ScrapeCachePolicyBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeCachePolicyManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_cache_policy_manager_instance = ScrapeCachePolicyManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapePathPattern
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapePathPatternDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_path_pattern_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_path_pattern_item.id)
        await self._process_core_data(scrape_path_pattern_item)
        await self._process_metadata(scrape_path_pattern_item)
        await self._initial_validation(scrape_path_pattern_item)
        self.initialized = True

    async def _process_core_data(self, scrape_path_pattern_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_path_pattern_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_path_pattern_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapePathPatternDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapePathPatternBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapePathPatternDTO
        super().__init__(ScrapePathPattern, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern):
        pass

    async def create_scrape_path_pattern(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_path_pattern(self, id):
        return await self.delete_item(id)

    async def get_scrape_path_pattern_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_path_pattern_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_path_pattern(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_path_pattern(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_path_patterns(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_path_patterns(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_path_pattern_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_path_patterns_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def get_scrape_path_pattern_with_scrape_configuration(self, id):
        return await self.get_item_with_related(id, 'scrape_configuration')

    async def get_scrape_path_patterns_with_scrape_configuration(self):
        return await self.get_items_with_related('scrape_configuration')

    async def get_scrape_path_pattern_with_scrape_path_pattern_override(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_override')

    async def get_scrape_path_patterns_with_scrape_path_pattern_override(self):
        return await self.get_items_with_related('scrape_path_pattern_override')

    async def get_scrape_path_pattern_with_scrape_path_pattern_cache_policy(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_cache_policy')

    async def get_scrape_path_patterns_with_scrape_path_pattern_cache_policy(self):
        return await self.get_items_with_related('scrape_path_pattern_cache_policy')

    async def load_scrape_path_patterns_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_path_patterns_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_path_patterns_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_path_pattern_ids(self):
        return self.active_item_ids



class ScrapePathPatternManager(ScrapePathPatternBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapePathPatternManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_path_pattern_manager_instance = ScrapePathPatternManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapePathPatternCachePolicy
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapePathPatternCachePolicyDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_path_pattern_cache_policy_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_path_pattern_cache_policy_item.id)
        await self._process_core_data(scrape_path_pattern_cache_policy_item)
        await self._process_metadata(scrape_path_pattern_cache_policy_item)
        await self._initial_validation(scrape_path_pattern_cache_policy_item)
        self.initialized = True

    async def _process_core_data(self, scrape_path_pattern_cache_policy_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_path_pattern_cache_policy_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_path_pattern_cache_policy_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapePathPatternCachePolicyDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapePathPatternCachePolicyBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapePathPatternCachePolicyDTO
        super().__init__(ScrapePathPatternCachePolicy, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern_cache_policy):
        pass

    async def create_scrape_path_pattern_cache_policy(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_path_pattern_cache_policy(self, id):
        return await self.delete_item(id)

    async def get_scrape_path_pattern_cache_policy_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_path_pattern_cache_policy_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_path_pattern_cache_policy(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_path_pattern_cache_policy(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_path_pattern_cache_policies(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_path_pattern_cache_policies(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_path_pattern_cache_policy_with_scrape_cache_policy(self, id):
        return await self.get_item_with_related(id, 'scrape_cache_policy')

    async def get_scrape_path_pattern_cache_policies_with_scrape_cache_policy(self):
        return await self.get_items_with_related('scrape_cache_policy')

    async def get_scrape_path_pattern_cache_policy_with_scrape_path_pattern(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern')

    async def get_scrape_path_pattern_cache_policies_with_scrape_path_pattern(self):
        return await self.get_items_with_related('scrape_path_pattern')

    async def get_scrape_path_pattern_cache_policy_with_scrape_cycle_tracker(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_tracker')

    async def get_scrape_path_pattern_cache_policies_with_scrape_cycle_tracker(self):
        return await self.get_items_with_related('scrape_cycle_tracker')

    async def get_scrape_path_pattern_cache_policy_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_path_pattern_cache_policies_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_path_pattern_cache_policies_by_scrape_cache_policy_id(self, scrape_cache_policy_id):
        return await self.load_items(scrape_cache_policy_id=scrape_cache_policy_id)

    async def filter_scrape_path_pattern_cache_policies_by_scrape_cache_policy_id(self, scrape_cache_policy_id):
        return await self.filter_items(scrape_cache_policy_id=scrape_cache_policy_id)

    async def load_scrape_path_pattern_cache_policies_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.load_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def filter_scrape_path_pattern_cache_policies_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.filter_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def load_scrape_path_pattern_cache_policies_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_path_pattern_cache_policy_ids(self):
        return self.active_item_ids



class ScrapePathPatternCachePolicyManager(ScrapePathPatternCachePolicyBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapePathPatternCachePolicyManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_path_pattern_cache_policy_manager_instance = ScrapePathPatternCachePolicyManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiModel
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiModelDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_model_item):
        '''Override the base initialization method.'''
        self.id = str(ai_model_item.id)
        await self._process_core_data(ai_model_item)
        await self._process_metadata(ai_model_item)
        await self._initial_validation(ai_model_item)
        self.initialized = True

    async def _process_core_data(self, ai_model_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_model_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_model_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiModelDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiModelBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiModelDTO
        super().__init__(AiModel, self.dto_class)

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

    async def get_ai_model_with_ai_provider(self, id):
        return await self.get_item_with_related(id, 'ai_provider')

    async def get_ai_models_with_ai_provider(self):
        return await self.get_items_with_related('ai_provider')

    async def get_ai_model_with_ai_model_endpoint(self, id):
        return await self.get_item_with_related(id, 'ai_model_endpoint')

    async def get_ai_models_with_ai_model_endpoint(self):
        return await self.get_items_with_related('ai_model_endpoint')

    async def get_ai_model_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_models_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def get_ai_model_with_recipe_model(self, id):
        return await self.get_item_with_related(id, 'recipe_model')

    async def get_ai_models_with_recipe_model(self):
        return await self.get_items_with_related('recipe_model')

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

    async def load_ai_models_by_model_class(self, model_class):
        return await self.load_items(model_class=model_class)

    async def filter_ai_models_by_model_class(self, model_class):
        return await self.filter_items(model_class=model_class)

    async def load_ai_models_by_model_provider(self, model_provider):
        return await self.load_items(model_provider=model_provider)

    async def filter_ai_models_by_model_provider(self, model_provider):
        return await self.filter_items(model_provider=model_provider)

    async def load_ai_models_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_model_ids(self):
        return self.active_item_ids



class AiModelManager(AiModelBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_model_manager_instance = AiModelManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Broker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class BrokerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, broker_item):
        '''Override the base initialization method.'''
        self.id = str(broker_item.id)
        await self._process_core_data(broker_item)
        await self._process_metadata(broker_item)
        await self._initial_validation(broker_item)
        self.initialized = True

    async def _process_core_data(self, broker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, broker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, broker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[BrokerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class BrokerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or BrokerDTO
        super().__init__(Broker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, broker):
        pass

    async def create_broker(self, **data):
        return await self.create_item(**data)

    async def delete_broker(self, id):
        return await self.delete_item(id)

    async def get_broker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_broker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_broker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_brokers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_brokers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_broker_with_data_input_component(self, id):
        return await self.get_item_with_related(id, 'data_input_component')

    async def get_brokers_with_data_input_component(self):
        return await self.get_items_with_related('data_input_component')

    async def get_broker_with_recipe_broker(self, id):
        return await self.get_item_with_related(id, 'recipe_broker')

    async def get_brokers_with_recipe_broker(self):
        return await self.get_items_with_related('recipe_broker')

    async def get_broker_with_registered_function(self, id):
        return await self.get_item_with_related(id, 'registered_function')

    async def get_brokers_with_registered_function(self):
        return await self.get_items_with_related('registered_function')

    async def get_broker_with_automation_boundary_broker(self, id):
        return await self.get_item_with_related(id, 'automation_boundary_broker')

    async def get_brokers_with_automation_boundary_broker(self):
        return await self.get_items_with_related('automation_boundary_broker')

    async def load_brokers_by_data_type(self, data_type):
        return await self.load_items(data_type=data_type)

    async def filter_brokers_by_data_type(self, data_type):
        return await self.filter_items(data_type=data_type)

    async def load_brokers_by_default_source(self, default_source):
        return await self.load_items(default_source=default_source)

    async def filter_brokers_by_default_source(self, default_source):
        return await self.filter_items(default_source=default_source)

    async def load_brokers_by_custom_source_component(self, custom_source_component):
        return await self.load_items(custom_source_component=custom_source_component)

    async def filter_brokers_by_custom_source_component(self, custom_source_component):
        return await self.filter_items(custom_source_component=custom_source_component)

    async def load_brokers_by_default_destination(self, default_destination):
        return await self.load_items(default_destination=default_destination)

    async def filter_brokers_by_default_destination(self, default_destination):
        return await self.filter_items(default_destination=default_destination)

    async def load_brokers_by_output_component(self, output_component):
        return await self.load_items(output_component=output_component)

    async def filter_brokers_by_output_component(self, output_component):
        return await self.filter_items(output_component=output_component)

    async def load_brokers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_broker_ids(self):
        return self.active_item_ids



class BrokerManager(BrokerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BrokerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

broker_manager_instance = BrokerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import DataOutputComponent
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class DataOutputComponentDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, data_output_component_item):
        '''Override the base initialization method.'''
        self.id = str(data_output_component_item.id)
        await self._process_core_data(data_output_component_item)
        await self._process_metadata(data_output_component_item)
        await self._initial_validation(data_output_component_item)
        self.initialized = True

    async def _process_core_data(self, data_output_component_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, data_output_component_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, data_output_component_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[DataOutputComponentDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class DataOutputComponentBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or DataOutputComponentDTO
        super().__init__(DataOutputComponent, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_output_component):
        pass

    async def create_data_output_component(self, **data):
        return await self.create_item(**data)

    async def delete_data_output_component(self, id):
        return await self.delete_item(id)

    async def get_data_output_component_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_data_output_component_by_id(self, id):
        return await self.load_by_id(id)

    async def load_data_output_component(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_data_output_component(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_data_output_components(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_data_output_components(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_data_output_component_with_data_broker(self, id):
        return await self.get_item_with_related(id, 'data_broker')

    async def get_data_output_components_with_data_broker(self):
        return await self.get_items_with_related('data_broker')

    async def load_data_output_components_by_component_type(self, component_type):
        return await self.load_items(component_type=component_type)

    async def filter_data_output_components_by_component_type(self, component_type):
        return await self.filter_items(component_type=component_type)

    async def load_data_output_components_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_data_output_component_ids(self):
        return self.active_item_ids



class DataOutputComponentManager(DataOutputComponentBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataOutputComponentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

data_output_component_manager_instance = DataOutputComponentManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FlashcardData
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FlashcardDataDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, flashcard_data_item):
        '''Override the base initialization method.'''
        self.id = str(flashcard_data_item.id)
        await self._process_core_data(flashcard_data_item)
        await self._process_metadata(flashcard_data_item)
        await self._initial_validation(flashcard_data_item)
        self.initialized = True

    async def _process_core_data(self, flashcard_data_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, flashcard_data_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, flashcard_data_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FlashcardDataDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FlashcardDataBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FlashcardDataDTO
        super().__init__(FlashcardData, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_data):
        pass

    async def create_flashcard_data(self, **data):
        return await self.create_item(**data)

    async def delete_flashcard_data(self, id):
        return await self.delete_item(id)

    async def get_flashcard_data_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_flashcard_data_by_id(self, id):
        return await self.load_by_id(id)

    async def load_flashcard_data(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_flashcard_data(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_flashcard_datas(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_flashcard_datas(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_flashcard_data_with_flashcard_history(self, id):
        return await self.get_item_with_related(id, 'flashcard_history')

    async def get_flashcard_datas_with_flashcard_history(self):
        return await self.get_items_with_related('flashcard_history')

    async def get_flashcard_data_with_flashcard_set_relations(self, id):
        return await self.get_item_with_related(id, 'flashcard_set_relations')

    async def get_flashcard_datas_with_flashcard_set_relations(self):
        return await self.get_items_with_related('flashcard_set_relations')

    async def get_flashcard_data_with_flashcard_images(self, id):
        return await self.get_item_with_related(id, 'flashcard_images')

    async def get_flashcard_datas_with_flashcard_images(self):
        return await self.get_items_with_related('flashcard_images')

    async def load_flashcard_datas_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_flashcard_datas_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_flashcard_datas_by_shared_with(self, shared_with):
        return await self.load_items(shared_with=shared_with)

    async def filter_flashcard_datas_by_shared_with(self, shared_with):
        return await self.filter_items(shared_with=shared_with)

    async def load_flashcard_datas_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_flashcard_data_ids(self):
        return self.active_item_ids



class FlashcardDataManager(FlashcardDataBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlashcardDataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

flashcard_data_manager_instance = FlashcardDataManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Organizations
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class OrganizationsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, organizations_item):
        '''Override the base initialization method.'''
        self.id = str(organizations_item.id)
        await self._process_core_data(organizations_item)
        await self._process_metadata(organizations_item)
        await self._initial_validation(organizations_item)
        self.initialized = True

    async def _process_core_data(self, organizations_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, organizations_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, organizations_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[OrganizationsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class OrganizationsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or OrganizationsDTO
        super().__init__(Organizations, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organizations):
        pass

    async def create_organizations(self, **data):
        return await self.create_item(**data)

    async def delete_organizations(self, id):
        return await self.delete_item(id)

    async def get_organizations_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_organizations_by_id(self, id):
        return await self.load_by_id(id)

    async def load_organizations(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_organizations(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_organization(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_organization(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_organizations_with_permissions(self, id):
        return await self.get_item_with_related(id, 'permissions')

    async def get_organization_with_permissions(self):
        return await self.get_items_with_related('permissions')

    async def get_organizations_with_organization_members(self, id):
        return await self.get_item_with_related(id, 'organization_members')

    async def get_organization_with_organization_members(self):
        return await self.get_items_with_related('organization_members')

    async def get_organizations_with_organization_invitations(self, id):
        return await self.get_item_with_related(id, 'organization_invitations')

    async def get_organization_with_organization_invitations(self):
        return await self.get_items_with_related('organization_invitations')

    async def load_organization_by_created_by(self, created_by):
        return await self.load_items(created_by=created_by)

    async def filter_organization_by_created_by(self, created_by):
        return await self.filter_items(created_by=created_by)

    async def load_organization_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_organizations_ids(self):
        return self.active_item_ids



class OrganizationsManager(OrganizationsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OrganizationsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

organizations_manager_instance = OrganizationsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Projects
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ProjectsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, projects_item):
        '''Override the base initialization method.'''
        self.id = str(projects_item.id)
        await self._process_core_data(projects_item)
        await self._process_metadata(projects_item)
        await self._initial_validation(projects_item)
        self.initialized = True

    async def _process_core_data(self, projects_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, projects_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, projects_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ProjectsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ProjectsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ProjectsDTO
        super().__init__(Projects, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, projects):
        pass

    async def create_projects(self, **data):
        return await self.create_item(**data)

    async def delete_projects(self, id):
        return await self.delete_item(id)

    async def get_projects_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_projects_by_id(self, id):
        return await self.load_by_id(id)

    async def load_projects(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_projects(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_project(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_project(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_projects_with_project_members(self, id):
        return await self.get_item_with_related(id, 'project_members')

    async def get_project_with_project_members(self):
        return await self.get_items_with_related('project_members')

    async def get_projects_with_tasks(self, id):
        return await self.get_item_with_related(id, 'tasks')

    async def get_project_with_tasks(self):
        return await self.get_items_with_related('tasks')

    async def load_project_by_created_by(self, created_by):
        return await self.load_items(created_by=created_by)

    async def filter_project_by_created_by(self, created_by):
        return await self.filter_items(created_by=created_by)

    async def load_project_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_projects_ids(self):
        return self.active_item_ids



class ProjectsManager(ProjectsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProjectsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

projects_manager_instance = ProjectsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeCycleTracker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeCycleTrackerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_cycle_tracker_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_cycle_tracker_item.id)
        await self._process_core_data(scrape_cycle_tracker_item)
        await self._process_metadata(scrape_cycle_tracker_item)
        await self._initial_validation(scrape_cycle_tracker_item)
        self.initialized = True

    async def _process_core_data(self, scrape_cycle_tracker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_cycle_tracker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_cycle_tracker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeCycleTrackerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeCycleTrackerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeCycleTrackerDTO
        super().__init__(ScrapeCycleTracker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cycle_tracker):
        pass

    async def create_scrape_cycle_tracker(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_cycle_tracker(self, id):
        return await self.delete_item(id)

    async def get_scrape_cycle_tracker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_cycle_tracker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_cycle_tracker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_cycle_tracker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_cycle_trackers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_cycle_trackers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_cycle_tracker_with_scrape_job(self, id):
        return await self.get_item_with_related(id, 'scrape_job')

    async def get_scrape_cycle_trackers_with_scrape_job(self):
        return await self.get_items_with_related('scrape_job')

    async def get_scrape_cycle_tracker_with_scrape_path_pattern_cache_policy(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_cache_policy')

    async def get_scrape_cycle_trackers_with_scrape_path_pattern_cache_policy(self):
        return await self.get_items_with_related('scrape_path_pattern_cache_policy')

    async def get_scrape_cycle_tracker_with_scrape_cycle_run(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_run')

    async def get_scrape_cycle_trackers_with_scrape_cycle_run(self):
        return await self.get_items_with_related('scrape_cycle_run')

    async def get_scrape_cycle_tracker_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_cycle_trackers_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_cycle_trackers_by_scrape_path_pattern_cache_policy_id(self, scrape_path_pattern_cache_policy_id):
        return await self.load_items(scrape_path_pattern_cache_policy_id=scrape_path_pattern_cache_policy_id)

    async def filter_scrape_cycle_trackers_by_scrape_path_pattern_cache_policy_id(self, scrape_path_pattern_cache_policy_id):
        return await self.filter_items(scrape_path_pattern_cache_policy_id=scrape_path_pattern_cache_policy_id)

    async def load_scrape_cycle_trackers_by_scrape_job_id(self, scrape_job_id):
        return await self.load_items(scrape_job_id=scrape_job_id)

    async def filter_scrape_cycle_trackers_by_scrape_job_id(self, scrape_job_id):
        return await self.filter_items(scrape_job_id=scrape_job_id)

    async def load_scrape_cycle_trackers_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_cycle_trackers_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_cycle_trackers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_cycle_tracker_ids(self):
        return self.active_item_ids



class ScrapeCycleTrackerManager(ScrapeCycleTrackerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeCycleTrackerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_cycle_tracker_manager_instance = ScrapeCycleTrackerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Tasks
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class TasksDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, tasks_item):
        '''Override the base initialization method.'''
        self.id = str(tasks_item.id)
        await self._process_core_data(tasks_item)
        await self._process_metadata(tasks_item)
        await self._initial_validation(tasks_item)
        self.initialized = True

    async def _process_core_data(self, tasks_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, tasks_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, tasks_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[TasksDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TasksBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TasksDTO
        super().__init__(Tasks, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tasks):
        pass

    async def create_tasks(self, **data):
        return await self.create_item(**data)

    async def delete_tasks(self, id):
        return await self.delete_item(id)

    async def get_tasks_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_tasks_by_id(self, id):
        return await self.load_by_id(id)

    async def load_tasks(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_tasks(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_task(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_task(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_tasks_with_projects(self, id):
        return await self.get_item_with_related(id, 'projects')

    async def get_task_with_projects(self):
        return await self.get_items_with_related('projects')

    async def get_tasks_with_task_assignments(self, id):
        return await self.get_item_with_related(id, 'task_assignments')

    async def get_task_with_task_assignments(self):
        return await self.get_items_with_related('task_assignments')

    async def get_tasks_with_task_attachments(self, id):
        return await self.get_item_with_related(id, 'task_attachments')

    async def get_task_with_task_attachments(self):
        return await self.get_items_with_related('task_attachments')

    async def get_tasks_with_task_comments(self, id):
        return await self.get_item_with_related(id, 'task_comments')

    async def get_task_with_task_comments(self):
        return await self.get_items_with_related('task_comments')

    async def load_task_by_project_id(self, project_id):
        return await self.load_items(project_id=project_id)

    async def filter_task_by_project_id(self, project_id):
        return await self.filter_items(project_id=project_id)

    async def load_task_by_created_by(self, created_by):
        return await self.load_items(created_by=created_by)

    async def filter_task_by_created_by(self, created_by):
        return await self.filter_items(created_by=created_by)

    async def load_task_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_tasks_ids(self):
        return self.active_item_ids



class TasksManager(TasksBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TasksManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

tasks_manager_instance = TasksManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiEndpoint
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiEndpointDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_endpoint_item):
        '''Override the base initialization method.'''
        self.id = str(ai_endpoint_item.id)
        await self._process_core_data(ai_endpoint_item)
        await self._process_metadata(ai_endpoint_item)
        await self._initial_validation(ai_endpoint_item)
        self.initialized = True

    async def _process_core_data(self, ai_endpoint_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_endpoint_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_endpoint_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiEndpointDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiEndpointBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiEndpointDTO
        super().__init__(AiEndpoint, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_endpoint):
        pass

    async def create_ai_endpoint(self, **data):
        return await self.create_item(**data)

    async def delete_ai_endpoint(self, id):
        return await self.delete_item(id)

    async def get_ai_endpoint_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_endpoint_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_endpoint(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_endpoint(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_endpoints(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_endpoints(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_endpoint_with_ai_model_endpoint(self, id):
        return await self.get_item_with_related(id, 'ai_model_endpoint')

    async def get_ai_endpoints_with_ai_model_endpoint(self):
        return await self.get_items_with_related('ai_model_endpoint')

    async def get_ai_endpoint_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_endpoints_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def load_ai_endpoints_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_endpoint_ids(self):
        return self.active_item_ids



class AiEndpointManager(AiEndpointBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiEndpointManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_endpoint_manager_instance = AiEndpointManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AutomationMatrix
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AutomationMatrixDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, automation_matrix_item):
        '''Override the base initialization method.'''
        self.id = str(automation_matrix_item.id)
        await self._process_core_data(automation_matrix_item)
        await self._process_metadata(automation_matrix_item)
        await self._initial_validation(automation_matrix_item)
        self.initialized = True

    async def _process_core_data(self, automation_matrix_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, automation_matrix_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, automation_matrix_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AutomationMatrixDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AutomationMatrixBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AutomationMatrixDTO
        super().__init__(AutomationMatrix, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, automation_matrix):
        pass

    async def create_automation_matrix(self, **data):
        return await self.create_item(**data)

    async def delete_automation_matrix(self, id):
        return await self.delete_item(id)

    async def get_automation_matrix_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_automation_matrix_by_id(self, id):
        return await self.load_by_id(id)

    async def load_automation_matrix(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_automation_matrix(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_automation_matrixes(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_automation_matrixes(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_automation_matrix_with_action(self, id):
        return await self.get_item_with_related(id, 'action')

    async def get_automation_matrixes_with_action(self):
        return await self.get_items_with_related('action')

    async def get_automation_matrix_with_automation_boundary_broker(self, id):
        return await self.get_item_with_related(id, 'automation_boundary_broker')

    async def get_automation_matrixes_with_automation_boundary_broker(self):
        return await self.get_items_with_related('automation_boundary_broker')

    async def load_automation_matrixes_by_cognition_matrices(self, cognition_matrices):
        return await self.load_items(cognition_matrices=cognition_matrices)

    async def filter_automation_matrixes_by_cognition_matrices(self, cognition_matrices):
        return await self.filter_items(cognition_matrices=cognition_matrices)

    async def load_automation_matrixes_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_automation_matrix_ids(self):
        return self.active_item_ids



class AutomationMatrixManager(AutomationMatrixBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AutomationMatrixManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

automation_matrix_manager_instance = AutomationMatrixManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import DataBroker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class DataBrokerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, data_broker_item):
        '''Override the base initialization method.'''
        self.id = str(data_broker_item.id)
        await self._process_core_data(data_broker_item)
        await self._process_metadata(data_broker_item)
        await self._initial_validation(data_broker_item)
        self.initialized = True

    async def _process_core_data(self, data_broker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, data_broker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, data_broker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[DataBrokerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class DataBrokerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or DataBrokerDTO
        super().__init__(DataBroker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, data_broker):
        pass

    async def create_data_broker(self, **data):
        return await self.create_item(**data)

    async def delete_data_broker(self, id):
        return await self.delete_item(id)

    async def get_data_broker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_data_broker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_data_broker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_data_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_data_brokers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_data_brokers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_data_broker_with_data_input_component(self, id):
        return await self.get_item_with_related(id, 'data_input_component')

    async def get_data_brokers_with_data_input_component(self):
        return await self.get_items_with_related('data_input_component')

    async def get_data_broker_with_data_output_component(self, id):
        return await self.get_item_with_related(id, 'data_output_component')

    async def get_data_brokers_with_data_output_component(self):
        return await self.get_items_with_related('data_output_component')

    async def get_data_broker_with_broker_value(self, id):
        return await self.get_item_with_related(id, 'broker_value')

    async def get_data_brokers_with_broker_value(self):
        return await self.get_items_with_related('broker_value')

    async def get_data_broker_with_message_broker(self, id):
        return await self.get_item_with_related(id, 'message_broker')

    async def get_data_brokers_with_message_broker(self):
        return await self.get_items_with_related('message_broker')

    async def load_data_brokers_by_data_type(self, data_type):
        return await self.load_items(data_type=data_type)

    async def filter_data_brokers_by_data_type(self, data_type):
        return await self.filter_items(data_type=data_type)

    async def load_data_brokers_by_input_component(self, input_component):
        return await self.load_items(input_component=input_component)

    async def filter_data_brokers_by_input_component(self, input_component):
        return await self.filter_items(input_component=input_component)

    async def load_data_brokers_by_color(self, color):
        return await self.load_items(color=color)

    async def filter_data_brokers_by_color(self, color):
        return await self.filter_items(color=color)

    async def load_data_brokers_by_output_component(self, output_component):
        return await self.load_items(output_component=output_component)

    async def filter_data_brokers_by_output_component(self, output_component):
        return await self.filter_items(output_component=output_component)

    async def load_data_brokers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_data_broker_ids(self):
        return self.active_item_ids



class DataBrokerManager(DataBrokerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataBrokerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

data_broker_manager_instance = DataBrokerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import MessageTemplate
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class MessageTemplateDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, message_template_item):
        '''Override the base initialization method.'''
        self.id = str(message_template_item.id)
        await self._process_core_data(message_template_item)
        await self._process_metadata(message_template_item)
        await self._initial_validation(message_template_item)
        self.initialized = True

    async def _process_core_data(self, message_template_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, message_template_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, message_template_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[MessageTemplateDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class MessageTemplateBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or MessageTemplateDTO
        super().__init__(MessageTemplate, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message_template):
        pass

    async def create_message_template(self, **data):
        return await self.create_item(**data)

    async def delete_message_template(self, id):
        return await self.delete_item(id)

    async def get_message_template_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_message_template_by_id(self, id):
        return await self.load_by_id(id)

    async def load_message_template(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_message_template(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_message_templates(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_message_templates(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_message_template_with_message_broker(self, id):
        return await self.get_item_with_related(id, 'message_broker')

    async def get_message_templates_with_message_broker(self):
        return await self.get_items_with_related('message_broker')

    async def get_message_template_with_recipe_message(self, id):
        return await self.get_item_with_related(id, 'recipe_message')

    async def get_message_templates_with_recipe_message(self):
        return await self.get_items_with_related('recipe_message')

    async def load_message_templates_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_message_templates_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_message_templates_by_type(self, type):
        return await self.load_items(type=type)

    async def filter_message_templates_by_type(self, type):
        return await self.filter_items(type=type)

    async def load_message_templates_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_message_template_ids(self):
        return self.active_item_ids



class MessageTemplateManager(MessageTemplateBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MessageTemplateManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

message_template_manager_instance = MessageTemplateManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RegisteredFunction
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RegisteredFunctionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, registered_function_item):
        '''Override the base initialization method.'''
        self.id = str(registered_function_item.id)
        await self._process_core_data(registered_function_item)
        await self._process_metadata(registered_function_item)
        await self._initial_validation(registered_function_item)
        self.initialized = True

    async def _process_core_data(self, registered_function_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, registered_function_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, registered_function_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RegisteredFunctionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RegisteredFunctionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RegisteredFunctionDTO
        super().__init__(RegisteredFunction, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, registered_function):
        pass

    async def create_registered_function(self, **data):
        return await self.create_item(**data)

    async def delete_registered_function(self, id):
        return await self.delete_item(id)

    async def get_registered_function_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_registered_function_by_id(self, id):
        return await self.load_by_id(id)

    async def load_registered_function(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_registered_function(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_registered_functions(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_registered_functions(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_registered_function_with_broker(self, id):
        return await self.get_item_with_related(id, 'broker')

    async def get_registered_functions_with_broker(self):
        return await self.get_items_with_related('broker')

    async def get_registered_function_with_system_function(self, id):
        return await self.get_item_with_related(id, 'system_function')

    async def get_registered_functions_with_system_function(self):
        return await self.get_items_with_related('system_function')

    async def get_registered_function_with_arg(self, id):
        return await self.get_item_with_related(id, 'arg')

    async def get_registered_functions_with_arg(self):
        return await self.get_items_with_related('arg')

    async def load_registered_functions_by_return_broker(self, return_broker):
        return await self.load_items(return_broker=return_broker)

    async def filter_registered_functions_by_return_broker(self, return_broker):
        return await self.filter_items(return_broker=return_broker)

    async def load_registered_functions_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_registered_function_ids(self):
        return self.active_item_ids



class RegisteredFunctionManager(RegisteredFunctionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RegisteredFunctionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

registered_function_manager_instance = RegisteredFunctionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeCycleRun
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeCycleRunDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_cycle_run_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_cycle_run_item.id)
        await self._process_core_data(scrape_cycle_run_item)
        await self._process_metadata(scrape_cycle_run_item)
        await self._initial_validation(scrape_cycle_run_item)
        self.initialized = True

    async def _process_core_data(self, scrape_cycle_run_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_cycle_run_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_cycle_run_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeCycleRunDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeCycleRunBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeCycleRunDTO
        super().__init__(ScrapeCycleRun, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_cycle_run):
        pass

    async def create_scrape_cycle_run(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_cycle_run(self, id):
        return await self.delete_item(id)

    async def get_scrape_cycle_run_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_cycle_run_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_cycle_run(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_cycle_run(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_cycle_runs(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_cycle_runs(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_cycle_run_with_scrape_cycle_tracker(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_tracker')

    async def get_scrape_cycle_runs_with_scrape_cycle_tracker(self):
        return await self.get_items_with_related('scrape_cycle_tracker')

    async def get_scrape_cycle_run_with_scrape_task(self, id):
        return await self.get_item_with_related(id, 'scrape_task')

    async def get_scrape_cycle_runs_with_scrape_task(self):
        return await self.get_items_with_related('scrape_task')

    async def get_scrape_cycle_run_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_cycle_runs_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_cycle_runs_by_scrape_cycle_tracker_id(self, scrape_cycle_tracker_id):
        return await self.load_items(scrape_cycle_tracker_id=scrape_cycle_tracker_id)

    async def filter_scrape_cycle_runs_by_scrape_cycle_tracker_id(self, scrape_cycle_tracker_id):
        return await self.filter_items(scrape_cycle_tracker_id=scrape_cycle_tracker_id)

    async def load_scrape_cycle_runs_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_cycle_run_ids(self):
        return self.active_item_ids



class ScrapeCycleRunManager(ScrapeCycleRunBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeCycleRunManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_cycle_run_manager_instance = ScrapeCycleRunManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeOverride
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeOverrideDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_override_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_override_item.id)
        await self._process_core_data(scrape_override_item)
        await self._process_metadata(scrape_override_item)
        await self._initial_validation(scrape_override_item)
        self.initialized = True

    async def _process_core_data(self, scrape_override_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_override_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_override_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeOverrideDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeOverrideBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeOverrideDTO
        super().__init__(ScrapeOverride, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_override):
        pass

    async def create_scrape_override(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_override(self, id):
        return await self.delete_item(id)

    async def get_scrape_override_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_override_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_override(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_override(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_overrides(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_overrides(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_override_with_scrape_override_value(self, id):
        return await self.get_item_with_related(id, 'scrape_override_value')

    async def get_scrape_overrides_with_scrape_override_value(self):
        return await self.get_items_with_related('scrape_override_value')

    async def get_scrape_override_with_scrape_path_pattern_override(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_override')

    async def get_scrape_overrides_with_scrape_path_pattern_override(self):
        return await self.get_items_with_related('scrape_path_pattern_override')

    async def load_scrape_overrides_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_overrides_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_overrides_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_override_ids(self):
        return self.active_item_ids



class ScrapeOverrideManager(ScrapeOverrideBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeOverrideManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_override_manager_instance = ScrapeOverrideManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeTask
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeTaskDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_task_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_task_item.id)
        await self._process_core_data(scrape_task_item)
        await self._process_metadata(scrape_task_item)
        await self._initial_validation(scrape_task_item)
        self.initialized = True

    async def _process_core_data(self, scrape_task_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_task_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_task_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeTaskDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeTaskBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeTaskDTO
        super().__init__(ScrapeTask, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_task):
        pass

    async def create_scrape_task(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_task(self, id):
        return await self.delete_item(id)

    async def get_scrape_task_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_task_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_task(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_task(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_tasks(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_tasks(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_task_with_scrape_cycle_run(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_run')

    async def get_scrape_tasks_with_scrape_cycle_run(self):
        return await self.get_items_with_related('scrape_cycle_run')

    async def get_scrape_task_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_tasks_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def get_scrape_task_with_scrape_job(self, id):
        return await self.get_item_with_related(id, 'scrape_job')

    async def get_scrape_tasks_with_scrape_job(self):
        return await self.get_items_with_related('scrape_job')

    async def get_scrape_task_with_scrape_task_response(self, id):
        return await self.get_item_with_related(id, 'scrape_task_response')

    async def get_scrape_tasks_with_scrape_task_response(self):
        return await self.get_items_with_related('scrape_task_response')

    async def get_scrape_task_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_tasks_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_tasks_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_tasks_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_tasks_by_scrape_job_id(self, scrape_job_id):
        return await self.load_items(scrape_job_id=scrape_job_id)

    async def filter_scrape_tasks_by_scrape_job_id(self, scrape_job_id):
        return await self.filter_items(scrape_job_id=scrape_job_id)

    async def load_scrape_tasks_by_scrape_cycle_run_id(self, scrape_cycle_run_id):
        return await self.load_items(scrape_cycle_run_id=scrape_cycle_run_id)

    async def filter_scrape_tasks_by_scrape_cycle_run_id(self, scrape_cycle_run_id):
        return await self.filter_items(scrape_cycle_run_id=scrape_cycle_run_id)

    async def load_scrape_tasks_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_tasks_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_tasks_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_task_ids(self):
        return self.active_item_ids



class ScrapeTaskManager(ScrapeTaskBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeTaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_task_manager_instance = ScrapeTaskManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import SystemFunction
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class SystemFunctionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, system_function_item):
        '''Override the base initialization method.'''
        self.id = str(system_function_item.id)
        await self._process_core_data(system_function_item)
        await self._process_metadata(system_function_item)
        await self._initial_validation(system_function_item)
        self.initialized = True

    async def _process_core_data(self, system_function_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, system_function_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, system_function_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[SystemFunctionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class SystemFunctionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or SystemFunctionDTO
        super().__init__(SystemFunction, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, system_function):
        pass

    async def create_system_function(self, **data):
        return await self.create_item(**data)

    async def delete_system_function(self, id):
        return await self.delete_item(id)

    async def get_system_function_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_system_function_by_id(self, id):
        return await self.load_by_id(id)

    async def load_system_function(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_system_function(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_system_functions(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_system_functions(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_system_function_with_registered_function(self, id):
        return await self.get_item_with_related(id, 'registered_function')

    async def get_system_functions_with_registered_function(self):
        return await self.get_items_with_related('registered_function')

    async def get_system_function_with_tool(self, id):
        return await self.get_item_with_related(id, 'tool')

    async def get_system_functions_with_tool(self):
        return await self.get_items_with_related('tool')

    async def get_system_function_with_recipe_function(self, id):
        return await self.get_item_with_related(id, 'recipe_function')

    async def get_system_functions_with_recipe_function(self):
        return await self.get_items_with_related('recipe_function')

    async def load_system_functions_by_rf_id(self, rf_id):
        return await self.load_items(rf_id=rf_id)

    async def filter_system_functions_by_rf_id(self, rf_id):
        return await self.filter_items(rf_id=rf_id)

    async def load_system_functions_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_system_function_ids(self):
        return self.active_item_ids



class SystemFunctionManager(SystemFunctionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SystemFunctionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

system_function_manager_instance = SystemFunctionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiSettings
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiSettingsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_settings_item):
        '''Override the base initialization method.'''
        self.id = str(ai_settings_item.id)
        await self._process_core_data(ai_settings_item)
        await self._process_metadata(ai_settings_item)
        await self._initial_validation(ai_settings_item)
        self.initialized = True

    async def _process_core_data(self, ai_settings_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_settings_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_settings_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiSettingsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiSettingsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiSettingsDTO
        super().__init__(AiSettings, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_settings):
        pass

    async def create_ai_settings(self, **data):
        return await self.create_item(**data)

    async def delete_ai_settings(self, id):
        return await self.delete_item(id)

    async def get_ai_settings_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_settings_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_settings(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_settings(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_setting(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_setting(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_settings_with_ai_endpoint(self, id):
        return await self.get_item_with_related(id, 'ai_endpoint')

    async def get_ai_setting_with_ai_endpoint(self):
        return await self.get_items_with_related('ai_endpoint')

    async def get_ai_settings_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_ai_setting_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def get_ai_settings_with_ai_provider(self, id):
        return await self.get_item_with_related(id, 'ai_provider')

    async def get_ai_setting_with_ai_provider(self):
        return await self.get_items_with_related('ai_provider')

    async def get_ai_settings_with_ai_agent(self, id):
        return await self.get_item_with_related(id, 'ai_agent')

    async def get_ai_setting_with_ai_agent(self):
        return await self.get_items_with_related('ai_agent')

    async def load_ai_setting_by_ai_endpoint(self, ai_endpoint):
        return await self.load_items(ai_endpoint=ai_endpoint)

    async def filter_ai_setting_by_ai_endpoint(self, ai_endpoint):
        return await self.filter_items(ai_endpoint=ai_endpoint)

    async def load_ai_setting_by_ai_provider(self, ai_provider):
        return await self.load_items(ai_provider=ai_provider)

    async def filter_ai_setting_by_ai_provider(self, ai_provider):
        return await self.filter_items(ai_provider=ai_provider)

    async def load_ai_setting_by_ai_model(self, ai_model):
        return await self.load_items(ai_model=ai_model)

    async def filter_ai_setting_by_ai_model(self, ai_model):
        return await self.filter_items(ai_model=ai_model)

    async def load_ai_setting_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_settings_ids(self):
        return self.active_item_ids



class AiSettingsManager(AiSettingsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiSettingsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_settings_manager_instance = AiSettingsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AudioLabel
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AudioLabelDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, audio_label_item):
        '''Override the base initialization method.'''
        self.id = str(audio_label_item.id)
        await self._process_core_data(audio_label_item)
        await self._process_metadata(audio_label_item)
        await self._initial_validation(audio_label_item)
        self.initialized = True

    async def _process_core_data(self, audio_label_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, audio_label_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, audio_label_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AudioLabelDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AudioLabelBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AudioLabelDTO
        super().__init__(AudioLabel, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_label):
        pass

    async def create_audio_label(self, **data):
        return await self.create_item(**data)

    async def delete_audio_label(self, id):
        return await self.delete_item(id)

    async def get_audio_label_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_audio_label_by_id(self, id):
        return await self.load_by_id(id)

    async def load_audio_label(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_audio_label(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_audio_labels(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_audio_labels(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_audio_label_with_audio_recording(self, id):
        return await self.get_item_with_related(id, 'audio_recording')

    async def get_audio_labels_with_audio_recording(self):
        return await self.get_items_with_related('audio_recording')

    async def load_audio_labels_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_audio_label_ids(self):
        return self.active_item_ids



class AudioLabelManager(AudioLabelBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AudioLabelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

audio_label_manager_instance = AudioLabelManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Category
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class CategoryDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, category_item):
        '''Override the base initialization method.'''
        self.id = str(category_item.id)
        await self._process_core_data(category_item)
        await self._process_metadata(category_item)
        await self._initial_validation(category_item)
        self.initialized = True

    async def _process_core_data(self, category_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, category_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, category_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[CategoryDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class CategoryBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or CategoryDTO
        super().__init__(Category, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, category):
        pass

    async def create_category(self, **data):
        return await self.create_item(**data)

    async def delete_category(self, id):
        return await self.delete_item(id)

    async def get_category_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_category_by_id(self, id):
        return await self.load_by_id(id)

    async def load_category(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_category(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_categories(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_categories(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_category_with_subcategory(self, id):
        return await self.get_item_with_related(id, 'subcategory')

    async def get_categories_with_subcategory(self):
        return await self.get_items_with_related('subcategory')

    async def load_categories_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_category_ids(self):
        return self.active_item_ids



class CategoryManager(CategoryBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CategoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

category_manager_instance = CategoryManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import CompiledRecipe
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class CompiledRecipeDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, compiled_recipe_item):
        '''Override the base initialization method.'''
        self.id = str(compiled_recipe_item.id)
        await self._process_core_data(compiled_recipe_item)
        await self._process_metadata(compiled_recipe_item)
        await self._initial_validation(compiled_recipe_item)
        self.initialized = True

    async def _process_core_data(self, compiled_recipe_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, compiled_recipe_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, compiled_recipe_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[CompiledRecipeDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class CompiledRecipeBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or CompiledRecipeDTO
        super().__init__(CompiledRecipe, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, compiled_recipe):
        pass

    async def create_compiled_recipe(self, **data):
        return await self.create_item(**data)

    async def delete_compiled_recipe(self, id):
        return await self.delete_item(id)

    async def get_compiled_recipe_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_compiled_recipe_by_id(self, id):
        return await self.load_by_id(id)

    async def load_compiled_recipe(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_compiled_recipe(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_compiled_recipes(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_compiled_recipes(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_compiled_recipe_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_compiled_recipes_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def get_compiled_recipe_with_applet(self, id):
        return await self.get_item_with_related(id, 'applet')

    async def get_compiled_recipes_with_applet(self):
        return await self.get_items_with_related('applet')

    async def load_compiled_recipes_by_recipe_id(self, recipe_id):
        return await self.load_items(recipe_id=recipe_id)

    async def filter_compiled_recipes_by_recipe_id(self, recipe_id):
        return await self.filter_items(recipe_id=recipe_id)

    async def load_compiled_recipes_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_compiled_recipes_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_compiled_recipes_by_version(self, version):
        return await self.load_items(version=version)

    async def filter_compiled_recipes_by_version(self, version):
        return await self.filter_items(version=version)

    async def load_compiled_recipes_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_compiled_recipe_ids(self):
        return self.active_item_ids



class CompiledRecipeManager(CompiledRecipeBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CompiledRecipeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

compiled_recipe_manager_instance = CompiledRecipeManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Conversation
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ConversationDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, conversation_item):
        '''Override the base initialization method.'''
        self.id = str(conversation_item.id)
        await self._process_core_data(conversation_item)
        await self._process_metadata(conversation_item)
        await self._initial_validation(conversation_item)
        self.initialized = True

    async def _process_core_data(self, conversation_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, conversation_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, conversation_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ConversationDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ConversationBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ConversationDTO
        super().__init__(Conversation, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, conversation):
        pass

    async def create_conversation(self, **data):
        return await self.create_item(**data)

    async def delete_conversation(self, id):
        return await self.delete_item(id)

    async def get_conversation_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_conversation_by_id(self, id):
        return await self.load_by_id(id)

    async def load_conversation(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_conversation(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_conversations(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_conversations(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_conversation_with_message(self, id):
        return await self.get_item_with_related(id, 'message')

    async def get_conversations_with_message(self):
        return await self.get_items_with_related('message')

    async def load_conversations_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_conversations_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_conversations_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_conversation_ids(self):
        return self.active_item_ids



class ConversationManager(ConversationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConversationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

conversation_manager_instance = ConversationManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import DisplayOption
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class DisplayOptionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, display_option_item):
        '''Override the base initialization method.'''
        self.id = str(display_option_item.id)
        await self._process_core_data(display_option_item)
        await self._process_metadata(display_option_item)
        await self._initial_validation(display_option_item)
        self.initialized = True

    async def _process_core_data(self, display_option_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, display_option_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, display_option_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[DisplayOptionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class DisplayOptionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or DisplayOptionDTO
        super().__init__(DisplayOption, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, display_option):
        pass

    async def create_display_option(self, **data):
        return await self.create_item(**data)

    async def delete_display_option(self, id):
        return await self.delete_item(id)

    async def get_display_option_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_display_option_by_id(self, id):
        return await self.load_by_id(id)

    async def load_display_option(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_display_option(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_display_options(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_display_options(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_display_option_with_recipe_display(self, id):
        return await self.get_item_with_related(id, 'recipe_display')

    async def get_display_options_with_recipe_display(self):
        return await self.get_items_with_related('recipe_display')

    async def load_display_options_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_display_option_ids(self):
        return self.active_item_ids



class DisplayOptionManager(DisplayOptionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DisplayOptionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

display_option_manager_instance = DisplayOptionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FlashcardSets
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FlashcardSetsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, flashcard_sets_item):
        '''Override the base initialization method.'''
        self.id = str(flashcard_sets_item.id)
        await self._process_core_data(flashcard_sets_item)
        await self._process_metadata(flashcard_sets_item)
        await self._initial_validation(flashcard_sets_item)
        self.initialized = True

    async def _process_core_data(self, flashcard_sets_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, flashcard_sets_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, flashcard_sets_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FlashcardSetsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FlashcardSetsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FlashcardSetsDTO
        super().__init__(FlashcardSets, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_sets):
        pass

    async def create_flashcard_sets(self, **data):
        return await self.create_item(**data)

    async def delete_flashcard_sets(self, id):
        return await self.delete_item(id)

    async def get_flashcard_sets_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_flashcard_sets_by_id(self, id):
        return await self.load_by_id(id)

    async def load_flashcard_sets(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_flashcard_sets(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_flashcard_set(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_flashcard_set(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_flashcard_sets_with_flashcard_set_relations(self, id):
        return await self.get_item_with_related(id, 'flashcard_set_relations')

    async def get_flashcard_set_with_flashcard_set_relations(self):
        return await self.get_items_with_related('flashcard_set_relations')

    async def load_flashcard_set_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_flashcard_set_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_flashcard_set_by_shared_with(self, shared_with):
        return await self.load_items(shared_with=shared_with)

    async def filter_flashcard_set_by_shared_with(self, shared_with):
        return await self.filter_items(shared_with=shared_with)

    async def load_flashcard_set_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_flashcard_sets_ids(self):
        return self.active_item_ids



class FlashcardSetsManager(FlashcardSetsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlashcardSetsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

flashcard_sets_manager_instance = FlashcardSetsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Processor
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ProcessorDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, processor_item):
        '''Override the base initialization method.'''
        self.id = str(processor_item.id)
        await self._process_core_data(processor_item)
        await self._process_metadata(processor_item)
        await self._initial_validation(processor_item)
        self.initialized = True

    async def _process_core_data(self, processor_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, processor_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, processor_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ProcessorDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ProcessorBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ProcessorDTO
        super().__init__(Processor, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, processor):
        pass

    async def create_processor(self, **data):
        return await self.create_item(**data)

    async def delete_processor(self, id):
        return await self.delete_item(id)

    async def get_processor_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_processor_by_id(self, id):
        return await self.load_by_id(id)

    async def load_processor(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_processor(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_processors(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_processors(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_processor_with_self_reference(self, id):
        return await self.get_item_with_related(id, 'self_reference')

    async def get_processors_with_self_reference(self):
        return await self.get_items_with_related('self_reference')

    async def get_processor_with_recipe_processor(self, id):
        return await self.get_item_with_related(id, 'recipe_processor')

    async def get_processors_with_recipe_processor(self):
        return await self.get_items_with_related('recipe_processor')

    async def load_processors_by_depends_default(self, depends_default):
        return await self.load_items(depends_default=depends_default)

    async def filter_processors_by_depends_default(self, depends_default):
        return await self.filter_items(depends_default=depends_default)

    async def load_processors_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_processor_ids(self):
        return self.active_item_ids



class ProcessorManager(ProcessorBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProcessorManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

processor_manager_instance = ProcessorManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeConfiguration
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeConfigurationDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_configuration_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_configuration_item.id)
        await self._process_core_data(scrape_configuration_item)
        await self._process_metadata(scrape_configuration_item)
        await self._initial_validation(scrape_configuration_item)
        self.initialized = True

    async def _process_core_data(self, scrape_configuration_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_configuration_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_configuration_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeConfigurationDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeConfigurationBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeConfigurationDTO
        super().__init__(ScrapeConfiguration, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_configuration):
        pass

    async def create_scrape_configuration(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_configuration(self, id):
        return await self.delete_item(id)

    async def get_scrape_configuration_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_configuration_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_configuration(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_configuration(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_configurations(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_configurations(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_configuration_with_scrape_path_pattern(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern')

    async def get_scrape_configurations_with_scrape_path_pattern(self):
        return await self.get_items_with_related('scrape_path_pattern')

    async def get_scrape_configuration_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_configurations_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_configurations_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.load_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def filter_scrape_configurations_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.filter_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def load_scrape_configurations_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_configurations_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_configurations_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_configuration_ids(self):
        return self.active_item_ids



class ScrapeConfigurationManager(ScrapeConfigurationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeConfigurationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_configuration_manager_instance = ScrapeConfigurationManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapePathPatternOverride
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapePathPatternOverrideDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_path_pattern_override_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_path_pattern_override_item.id)
        await self._process_core_data(scrape_path_pattern_override_item)
        await self._process_metadata(scrape_path_pattern_override_item)
        await self._initial_validation(scrape_path_pattern_override_item)
        self.initialized = True

    async def _process_core_data(self, scrape_path_pattern_override_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_path_pattern_override_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_path_pattern_override_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapePathPatternOverrideDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapePathPatternOverrideBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapePathPatternOverrideDTO
        super().__init__(ScrapePathPatternOverride, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_path_pattern_override):
        pass

    async def create_scrape_path_pattern_override(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_path_pattern_override(self, id):
        return await self.delete_item(id)

    async def get_scrape_path_pattern_override_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_path_pattern_override_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_path_pattern_override(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_path_pattern_override(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_path_pattern_overrides(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_path_pattern_overrides(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_path_pattern_override_with_scrape_override(self, id):
        return await self.get_item_with_related(id, 'scrape_override')

    async def get_scrape_path_pattern_overrides_with_scrape_override(self):
        return await self.get_items_with_related('scrape_override')

    async def get_scrape_path_pattern_override_with_scrape_path_pattern(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern')

    async def get_scrape_path_pattern_overrides_with_scrape_path_pattern(self):
        return await self.get_items_with_related('scrape_path_pattern')

    async def get_scrape_path_pattern_override_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_path_pattern_overrides_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_path_pattern_overrides_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.load_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def filter_scrape_path_pattern_overrides_by_scrape_path_pattern_id(self, scrape_path_pattern_id):
        return await self.filter_items(scrape_path_pattern_id=scrape_path_pattern_id)

    async def load_scrape_path_pattern_overrides_by_scrape_override_id(self, scrape_override_id):
        return await self.load_items(scrape_override_id=scrape_override_id)

    async def filter_scrape_path_pattern_overrides_by_scrape_override_id(self, scrape_override_id):
        return await self.filter_items(scrape_override_id=scrape_override_id)

    async def load_scrape_path_pattern_overrides_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_path_pattern_overrides_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_path_pattern_overrides_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_path_pattern_override_ids(self):
        return self.active_item_ids



class ScrapePathPatternOverrideManager(ScrapePathPatternOverrideBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapePathPatternOverrideManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_path_pattern_override_manager_instance = ScrapePathPatternOverrideManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeTaskResponse
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeTaskResponseDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_task_response_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_task_response_item.id)
        await self._process_core_data(scrape_task_response_item)
        await self._process_metadata(scrape_task_response_item)
        await self._initial_validation(scrape_task_response_item)
        self.initialized = True

    async def _process_core_data(self, scrape_task_response_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_task_response_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_task_response_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeTaskResponseDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeTaskResponseBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeTaskResponseDTO
        super().__init__(ScrapeTaskResponse, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_task_response):
        pass

    async def create_scrape_task_response(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_task_response(self, id):
        return await self.delete_item(id)

    async def get_scrape_task_response_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_task_response_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_task_response(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_task_response(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_task_responses(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_task_responses(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_task_response_with_scrape_task(self, id):
        return await self.get_item_with_related(id, 'scrape_task')

    async def get_scrape_task_responses_with_scrape_task(self):
        return await self.get_items_with_related('scrape_task')

    async def get_scrape_task_response_with_scrape_parsed_page(self, id):
        return await self.get_item_with_related(id, 'scrape_parsed_page')

    async def get_scrape_task_responses_with_scrape_parsed_page(self):
        return await self.get_items_with_related('scrape_parsed_page')

    async def load_scrape_task_responses_by_scrape_task_id(self, scrape_task_id):
        return await self.load_items(scrape_task_id=scrape_task_id)

    async def filter_scrape_task_responses_by_scrape_task_id(self, scrape_task_id):
        return await self.filter_items(scrape_task_id=scrape_task_id)

    async def load_scrape_task_responses_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_task_responses_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_task_responses_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_task_response_ids(self):
        return self.active_item_ids



class ScrapeTaskResponseManager(ScrapeTaskResponseBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeTaskResponseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_task_response_manager_instance = ScrapeTaskResponseManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Subcategory
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class SubcategoryDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, subcategory_item):
        '''Override the base initialization method.'''
        self.id = str(subcategory_item.id)
        await self._process_core_data(subcategory_item)
        await self._process_metadata(subcategory_item)
        await self._initial_validation(subcategory_item)
        self.initialized = True

    async def _process_core_data(self, subcategory_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, subcategory_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, subcategory_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[SubcategoryDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class SubcategoryBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or SubcategoryDTO
        super().__init__(Subcategory, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, subcategory):
        pass

    async def create_subcategory(self, **data):
        return await self.create_item(**data)

    async def delete_subcategory(self, id):
        return await self.delete_item(id)

    async def get_subcategory_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_subcategory_by_id(self, id):
        return await self.load_by_id(id)

    async def load_subcategory(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_subcategory(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_subcategories(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_subcategories(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_subcategory_with_category(self, id):
        return await self.get_item_with_related(id, 'category')

    async def get_subcategories_with_category(self):
        return await self.get_items_with_related('category')

    async def get_subcategory_with_applet(self, id):
        return await self.get_item_with_related(id, 'applet')

    async def get_subcategories_with_applet(self):
        return await self.get_items_with_related('applet')

    async def load_subcategories_by_category_id(self, category_id):
        return await self.load_items(category_id=category_id)

    async def filter_subcategories_by_category_id(self, category_id):
        return await self.filter_items(category_id=category_id)

    async def load_subcategories_by_features(self, features):
        return await self.load_items(features=features)

    async def filter_subcategories_by_features(self, features):
        return await self.filter_items(features=features)

    async def load_subcategories_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_subcategory_ids(self):
        return self.active_item_ids



class SubcategoryManager(SubcategoryBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SubcategoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

subcategory_manager_instance = SubcategoryManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Tool
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ToolDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, tool_item):
        '''Override the base initialization method.'''
        self.id = str(tool_item.id)
        await self._process_core_data(tool_item)
        await self._process_metadata(tool_item)
        await self._initial_validation(tool_item)
        self.initialized = True

    async def _process_core_data(self, tool_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, tool_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, tool_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ToolDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ToolBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ToolDTO
        super().__init__(Tool, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tool):
        pass

    async def create_tool(self, **data):
        return await self.create_item(**data)

    async def delete_tool(self, id):
        return await self.delete_item(id)

    async def get_tool_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_tool_by_id(self, id):
        return await self.load_by_id(id)

    async def load_tool(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_tool(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_tools(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_tools(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_tool_with_system_function(self, id):
        return await self.get_item_with_related(id, 'system_function')

    async def get_tools_with_system_function(self):
        return await self.get_items_with_related('system_function')

    async def get_tool_with_recipe_tool(self, id):
        return await self.get_item_with_related(id, 'recipe_tool')

    async def get_tools_with_recipe_tool(self):
        return await self.get_items_with_related('recipe_tool')

    async def load_tools_by_system_function(self, system_function):
        return await self.load_items(system_function=system_function)

    async def filter_tools_by_system_function(self, system_function):
        return await self.filter_items(system_function=system_function)

    async def load_tools_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_tool_ids(self):
        return self.active_item_ids



class ToolManager(ToolBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ToolManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

tool_manager_instance = ToolManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Transformer
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class TransformerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, transformer_item):
        '''Override the base initialization method.'''
        self.id = str(transformer_item.id)
        await self._process_core_data(transformer_item)
        await self._process_metadata(transformer_item)
        await self._initial_validation(transformer_item)
        self.initialized = True

    async def _process_core_data(self, transformer_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, transformer_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, transformer_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[TransformerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TransformerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TransformerDTO
        super().__init__(Transformer, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, transformer):
        pass

    async def create_transformer(self, **data):
        return await self.create_item(**data)

    async def delete_transformer(self, id):
        return await self.delete_item(id)

    async def get_transformer_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_transformer_by_id(self, id):
        return await self.load_by_id(id)

    async def load_transformer(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_transformer(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_transformers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_transformers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_transformer_with_action(self, id):
        return await self.get_item_with_related(id, 'action')

    async def get_transformers_with_action(self):
        return await self.get_items_with_related('action')

    async def load_transformers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_transformer_ids(self):
        return self.active_item_ids



class TransformerManager(TransformerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TransformerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

transformer_manager_instance = TransformerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import WcClaim
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class WcClaimDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, wc_claim_item):
        '''Override the base initialization method.'''
        self.id = str(wc_claim_item.id)
        await self._process_core_data(wc_claim_item)
        await self._process_metadata(wc_claim_item)
        await self._initial_validation(wc_claim_item)
        self.initialized = True

    async def _process_core_data(self, wc_claim_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, wc_claim_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, wc_claim_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[WcClaimDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class WcClaimBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or WcClaimDTO
        super().__init__(WcClaim, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_claim):
        pass

    async def create_wc_claim(self, **data):
        return await self.create_item(**data)

    async def delete_wc_claim(self, id):
        return await self.delete_item(id)

    async def get_wc_claim_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_wc_claim_by_id(self, id):
        return await self.load_by_id(id)

    async def load_wc_claim(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_wc_claim(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_wc_claims(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_wc_claims(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_wc_claim_with_wc_report(self, id):
        return await self.get_item_with_related(id, 'wc_report')

    async def get_wc_claims_with_wc_report(self):
        return await self.get_items_with_related('wc_report')

    async def load_wc_claims_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_wc_claim_ids(self):
        return self.active_item_ids



class WcClaimManager(WcClaimBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WcClaimManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

wc_claim_manager_instance = WcClaimManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import WcImpairmentDefinition
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class WcImpairmentDefinitionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, wc_impairment_definition_item):
        '''Override the base initialization method.'''
        self.id = str(wc_impairment_definition_item.id)
        await self._process_core_data(wc_impairment_definition_item)
        await self._process_metadata(wc_impairment_definition_item)
        await self._initial_validation(wc_impairment_definition_item)
        self.initialized = True

    async def _process_core_data(self, wc_impairment_definition_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, wc_impairment_definition_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, wc_impairment_definition_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[WcImpairmentDefinitionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class WcImpairmentDefinitionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or WcImpairmentDefinitionDTO
        super().__init__(WcImpairmentDefinition, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_impairment_definition):
        pass

    async def create_wc_impairment_definition(self, **data):
        return await self.create_item(**data)

    async def delete_wc_impairment_definition(self, id):
        return await self.delete_item(id)

    async def get_wc_impairment_definition_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_wc_impairment_definition_by_id(self, id):
        return await self.load_by_id(id)

    async def load_wc_impairment_definition(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_wc_impairment_definition(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_wc_impairment_definitions(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_wc_impairment_definitions(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_wc_impairment_definition_with_wc_injury(self, id):
        return await self.get_item_with_related(id, 'wc_injury')

    async def get_wc_impairment_definitions_with_wc_injury(self):
        return await self.get_items_with_related('wc_injury')

    async def load_wc_impairment_definitions_by_finger_type(self, finger_type):
        return await self.load_items(finger_type=finger_type)

    async def filter_wc_impairment_definitions_by_finger_type(self, finger_type):
        return await self.filter_items(finger_type=finger_type)

    async def load_wc_impairment_definitions_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_wc_impairment_definition_ids(self):
        return self.active_item_ids



class WcImpairmentDefinitionManager(WcImpairmentDefinitionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WcImpairmentDefinitionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

wc_impairment_definition_manager_instance = WcImpairmentDefinitionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import WcReport
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class WcReportDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, wc_report_item):
        '''Override the base initialization method.'''
        self.id = str(wc_report_item.id)
        await self._process_core_data(wc_report_item)
        await self._process_metadata(wc_report_item)
        await self._initial_validation(wc_report_item)
        self.initialized = True

    async def _process_core_data(self, wc_report_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, wc_report_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, wc_report_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[WcReportDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class WcReportBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or WcReportDTO
        super().__init__(WcReport, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_report):
        pass

    async def create_wc_report(self, **data):
        return await self.create_item(**data)

    async def delete_wc_report(self, id):
        return await self.delete_item(id)

    async def get_wc_report_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_wc_report_by_id(self, id):
        return await self.load_by_id(id)

    async def load_wc_report(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_wc_report(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_wc_reports(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_wc_reports(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_wc_report_with_wc_claim(self, id):
        return await self.get_item_with_related(id, 'wc_claim')

    async def get_wc_reports_with_wc_claim(self):
        return await self.get_items_with_related('wc_claim')

    async def get_wc_report_with_wc_injury(self, id):
        return await self.get_item_with_related(id, 'wc_injury')

    async def get_wc_reports_with_wc_injury(self):
        return await self.get_items_with_related('wc_injury')

    async def load_wc_reports_by_claim_id(self, claim_id):
        return await self.load_items(claim_id=claim_id)

    async def filter_wc_reports_by_claim_id(self, claim_id):
        return await self.filter_items(claim_id=claim_id)

    async def load_wc_reports_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_wc_report_ids(self):
        return self.active_item_ids



class WcReportManager(WcReportBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WcReportManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

wc_report_manager_instance = WcReportManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Action
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ActionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, action_item):
        '''Override the base initialization method.'''
        self.id = str(action_item.id)
        await self._process_core_data(action_item)
        await self._process_metadata(action_item)
        await self._initial_validation(action_item)
        self.initialized = True

    async def _process_core_data(self, action_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, action_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, action_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ActionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ActionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ActionDTO
        super().__init__(Action, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, action):
        pass

    async def create_action(self, **data):
        return await self.create_item(**data)

    async def delete_action(self, id):
        return await self.delete_item(id)

    async def get_action_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_action_by_id(self, id):
        return await self.load_by_id(id)

    async def load_action(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_action(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_actions(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_actions(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_action_with_automation_matrix(self, id):
        return await self.get_item_with_related(id, 'automation_matrix')

    async def get_actions_with_automation_matrix(self):
        return await self.get_items_with_related('automation_matrix')

    async def get_action_with_transformer(self, id):
        return await self.get_item_with_related(id, 'transformer')

    async def get_actions_with_transformer(self):
        return await self.get_items_with_related('transformer')

    async def load_actions_by_matrix(self, matrix):
        return await self.load_items(matrix=matrix)

    async def filter_actions_by_matrix(self, matrix):
        return await self.filter_items(matrix=matrix)

    async def load_actions_by_transformer(self, transformer):
        return await self.load_items(transformer=transformer)

    async def filter_actions_by_transformer(self, transformer):
        return await self.filter_items(transformer=transformer)

    async def load_actions_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_action_ids(self):
        return self.active_item_ids



class ActionManager(ActionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

action_manager_instance = ActionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Admins
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AdminsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, admins_item):
        '''Override the base initialization method.'''
        self.id = str(admins_item.id)
        await self._process_core_data(admins_item)
        await self._process_metadata(admins_item)
        await self._initial_validation(admins_item)
        self.initialized = True

    async def _process_core_data(self, admins_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, admins_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, admins_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AdminsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AdminsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AdminsDTO
        super().__init__(Admins, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, admins):
        pass

    async def create_admins(self, **data):
        return await self.create_item(**data)

    async def delete_admins(self, id):
        return await self.delete_item(id)

    async def get_admins_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_admins_by_id(self, id):
        return await self.load_by_id(id)

    async def load_admins(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_admins(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_admin(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_admin(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_admin_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_admin_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_admin_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_admins_ids(self):
        return self.active_item_ids



class AdminsManager(AdminsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AdminsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

admins_manager_instance = AdminsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiAgent
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiAgentDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_agent_item):
        '''Override the base initialization method.'''
        self.id = str(ai_agent_item.id)
        await self._process_core_data(ai_agent_item)
        await self._process_metadata(ai_agent_item)
        await self._initial_validation(ai_agent_item)
        self.initialized = True

    async def _process_core_data(self, ai_agent_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_agent_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_agent_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiAgentDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiAgentBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiAgentDTO
        super().__init__(AiAgent, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_agent):
        pass

    async def create_ai_agent(self, **data):
        return await self.create_item(**data)

    async def delete_ai_agent(self, id):
        return await self.delete_item(id)

    async def get_ai_agent_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_agent_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_agent(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_agent(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_agents(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_agents(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_agent_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_agents_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def get_ai_agent_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_ai_agents_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_ai_agents_by_recipe_id(self, recipe_id):
        return await self.load_items(recipe_id=recipe_id)

    async def filter_ai_agents_by_recipe_id(self, recipe_id):
        return await self.filter_items(recipe_id=recipe_id)

    async def load_ai_agents_by_ai_settings_id(self, ai_settings_id):
        return await self.load_items(ai_settings_id=ai_settings_id)

    async def filter_ai_agents_by_ai_settings_id(self, ai_settings_id):
        return await self.filter_items(ai_settings_id=ai_settings_id)

    async def load_ai_agents_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_agent_ids(self):
        return self.active_item_ids



class AiAgentManager(AiAgentBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiAgentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_agent_manager_instance = AiAgentManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiModelEndpoint
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiModelEndpointDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_model_endpoint_item):
        '''Override the base initialization method.'''
        self.id = str(ai_model_endpoint_item.id)
        await self._process_core_data(ai_model_endpoint_item)
        await self._process_metadata(ai_model_endpoint_item)
        await self._initial_validation(ai_model_endpoint_item)
        self.initialized = True

    async def _process_core_data(self, ai_model_endpoint_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_model_endpoint_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_model_endpoint_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiModelEndpointDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiModelEndpointBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiModelEndpointDTO
        super().__init__(AiModelEndpoint, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_model_endpoint):
        pass

    async def create_ai_model_endpoint(self, **data):
        return await self.create_item(**data)

    async def delete_ai_model_endpoint(self, id):
        return await self.delete_item(id)

    async def get_ai_model_endpoint_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_model_endpoint_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_model_endpoint(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_model_endpoint(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_model_endpoints(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_model_endpoints(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_model_endpoint_with_ai_endpoint(self, id):
        return await self.get_item_with_related(id, 'ai_endpoint')

    async def get_ai_model_endpoints_with_ai_endpoint(self):
        return await self.get_items_with_related('ai_endpoint')

    async def get_ai_model_endpoint_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_ai_model_endpoints_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def load_ai_model_endpoints_by_ai_model_id(self, ai_model_id):
        return await self.load_items(ai_model_id=ai_model_id)

    async def filter_ai_model_endpoints_by_ai_model_id(self, ai_model_id):
        return await self.filter_items(ai_model_id=ai_model_id)

    async def load_ai_model_endpoints_by_ai_endpoint_id(self, ai_endpoint_id):
        return await self.load_items(ai_endpoint_id=ai_endpoint_id)

    async def filter_ai_model_endpoints_by_ai_endpoint_id(self, ai_endpoint_id):
        return await self.filter_items(ai_endpoint_id=ai_endpoint_id)

    async def load_ai_model_endpoints_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_model_endpoint_ids(self):
        return self.active_item_ids



class AiModelEndpointManager(AiModelEndpointBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiModelEndpointManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_model_endpoint_manager_instance = AiModelEndpointManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AiTrainingData
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AiTrainingDataDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, ai_training_data_item):
        '''Override the base initialization method.'''
        self.id = str(ai_training_data_item.id)
        await self._process_core_data(ai_training_data_item)
        await self._process_metadata(ai_training_data_item)
        await self._initial_validation(ai_training_data_item)
        self.initialized = True

    async def _process_core_data(self, ai_training_data_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, ai_training_data_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, ai_training_data_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AiTrainingDataDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AiTrainingDataBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AiTrainingDataDTO
        super().__init__(AiTrainingData, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, ai_training_data):
        pass

    async def create_ai_training_data(self, **data):
        return await self.create_item(**data)

    async def delete_ai_training_data(self, id):
        return await self.delete_item(id)

    async def get_ai_training_data_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_training_data_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_training_data(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_training_data(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_ai_training_datas(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_training_datas(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_ai_training_datas_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_ai_training_datas_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_ai_training_datas_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_training_data_ids(self):
        return self.active_item_ids



class AiTrainingDataManager(AiTrainingDataBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiTrainingDataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

ai_training_data_manager_instance = AiTrainingDataManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Applet
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AppletDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, applet_item):
        '''Override the base initialization method.'''
        self.id = str(applet_item.id)
        await self._process_core_data(applet_item)
        await self._process_metadata(applet_item)
        await self._initial_validation(applet_item)
        self.initialized = True

    async def _process_core_data(self, applet_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, applet_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, applet_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AppletDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AppletBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AppletDTO
        super().__init__(Applet, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, applet):
        pass

    async def create_applet(self, **data):
        return await self.create_item(**data)

    async def delete_applet(self, id):
        return await self.delete_item(id)

    async def get_applet_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_applet_by_id(self, id):
        return await self.load_by_id(id)

    async def load_applet(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_applet(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_applets(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_applets(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_applet_with_compiled_recipe(self, id):
        return await self.get_item_with_related(id, 'compiled_recipe')

    async def get_applets_with_compiled_recipe(self):
        return await self.get_items_with_related('compiled_recipe')

    async def get_applet_with_subcategory(self, id):
        return await self.get_item_with_related(id, 'subcategory')

    async def get_applets_with_subcategory(self):
        return await self.get_items_with_related('subcategory')

    async def load_applets_by_type(self, type):
        return await self.load_items(type=type)

    async def filter_applets_by_type(self, type):
        return await self.filter_items(type=type)

    async def load_applets_by_compiled_recipe_id(self, compiled_recipe_id):
        return await self.load_items(compiled_recipe_id=compiled_recipe_id)

    async def filter_applets_by_compiled_recipe_id(self, compiled_recipe_id):
        return await self.filter_items(compiled_recipe_id=compiled_recipe_id)

    async def load_applets_by_subcategory_id(self, subcategory_id):
        return await self.load_items(subcategory_id=subcategory_id)

    async def filter_applets_by_subcategory_id(self, subcategory_id):
        return await self.filter_items(subcategory_id=subcategory_id)

    async def load_applets_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_applet_ids(self):
        return self.active_item_ids



class AppletManager(AppletBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AppletManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

applet_manager_instance = AppletManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Arg
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ArgDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, arg_item):
        '''Override the base initialization method.'''
        self.id = str(arg_item.id)
        await self._process_core_data(arg_item)
        await self._process_metadata(arg_item)
        await self._initial_validation(arg_item)
        self.initialized = True

    async def _process_core_data(self, arg_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, arg_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, arg_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ArgDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ArgBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ArgDTO
        super().__init__(Arg, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, arg):
        pass

    async def create_arg(self, **data):
        return await self.create_item(**data)

    async def delete_arg(self, id):
        return await self.delete_item(id)

    async def get_arg_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_arg_by_id(self, id):
        return await self.load_by_id(id)

    async def load_arg(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_arg(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_args(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_args(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_arg_with_registered_function(self, id):
        return await self.get_item_with_related(id, 'registered_function')

    async def get_args_with_registered_function(self):
        return await self.get_items_with_related('registered_function')

    async def load_args_by_data_type(self, data_type):
        return await self.load_items(data_type=data_type)

    async def filter_args_by_data_type(self, data_type):
        return await self.filter_items(data_type=data_type)

    async def load_args_by_registered_function(self, registered_function):
        return await self.load_items(registered_function=registered_function)

    async def filter_args_by_registered_function(self, registered_function):
        return await self.filter_items(registered_function=registered_function)

    async def load_args_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_arg_ids(self):
        return self.active_item_ids



class ArgManager(ArgBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ArgManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

arg_manager_instance = ArgManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AudioRecording
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AudioRecordingDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, audio_recording_item):
        '''Override the base initialization method.'''
        self.id = str(audio_recording_item.id)
        await self._process_core_data(audio_recording_item)
        await self._process_metadata(audio_recording_item)
        await self._initial_validation(audio_recording_item)
        self.initialized = True

    async def _process_core_data(self, audio_recording_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, audio_recording_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, audio_recording_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AudioRecordingDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AudioRecordingBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AudioRecordingDTO
        super().__init__(AudioRecording, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_recording):
        pass

    async def create_audio_recording(self, **data):
        return await self.create_item(**data)

    async def delete_audio_recording(self, id):
        return await self.delete_item(id)

    async def get_audio_recording_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_audio_recording_by_id(self, id):
        return await self.load_by_id(id)

    async def load_audio_recording(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_audio_recording(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_audio_recordings(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_audio_recordings(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_audio_recording_with_audio_label(self, id):
        return await self.get_item_with_related(id, 'audio_label')

    async def get_audio_recordings_with_audio_label(self):
        return await self.get_items_with_related('audio_label')

    async def load_audio_recordings_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_audio_recordings_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_audio_recordings_by_label(self, label):
        return await self.load_items(label=label)

    async def filter_audio_recordings_by_label(self, label):
        return await self.filter_items(label=label)

    async def load_audio_recordings_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_audio_recording_ids(self):
        return self.active_item_ids



class AudioRecordingManager(AudioRecordingBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AudioRecordingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

audio_recording_manager_instance = AudioRecordingManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AudioRecordingUsers
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AudioRecordingUsersDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, audio_recording_users_item):
        '''Override the base initialization method.'''
        self.id = str(audio_recording_users_item.id)
        await self._process_core_data(audio_recording_users_item)
        await self._process_metadata(audio_recording_users_item)
        await self._initial_validation(audio_recording_users_item)
        self.initialized = True

    async def _process_core_data(self, audio_recording_users_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, audio_recording_users_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, audio_recording_users_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AudioRecordingUsersDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AudioRecordingUsersBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AudioRecordingUsersDTO
        super().__init__(AudioRecordingUsers, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, audio_recording_users):
        pass

    async def create_audio_recording_users(self, **data):
        return await self.create_item(**data)

    async def delete_audio_recording_users(self, id):
        return await self.delete_item(id)

    async def get_audio_recording_users_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_audio_recording_users_by_id(self, id):
        return await self.load_by_id(id)

    async def load_audio_recording_users(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_audio_recording_users(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_audio_recording_user(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_audio_recording_user(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_audio_recording_user_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_audio_recording_users_ids(self):
        return self.active_item_ids



class AudioRecordingUsersManager(AudioRecordingUsersBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AudioRecordingUsersManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

audio_recording_users_manager_instance = AudioRecordingUsersManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import AutomationBoundaryBroker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class AutomationBoundaryBrokerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, automation_boundary_broker_item):
        '''Override the base initialization method.'''
        self.id = str(automation_boundary_broker_item.id)
        await self._process_core_data(automation_boundary_broker_item)
        await self._process_metadata(automation_boundary_broker_item)
        await self._initial_validation(automation_boundary_broker_item)
        self.initialized = True

    async def _process_core_data(self, automation_boundary_broker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, automation_boundary_broker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, automation_boundary_broker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[AutomationBoundaryBrokerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class AutomationBoundaryBrokerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or AutomationBoundaryBrokerDTO
        super().__init__(AutomationBoundaryBroker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, automation_boundary_broker):
        pass

    async def create_automation_boundary_broker(self, **data):
        return await self.create_item(**data)

    async def delete_automation_boundary_broker(self, id):
        return await self.delete_item(id)

    async def get_automation_boundary_broker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_automation_boundary_broker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_automation_boundary_broker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_automation_boundary_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_automation_boundary_brokers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_automation_boundary_brokers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_automation_boundary_broker_with_broker(self, id):
        return await self.get_item_with_related(id, 'broker')

    async def get_automation_boundary_brokers_with_broker(self):
        return await self.get_items_with_related('broker')

    async def get_automation_boundary_broker_with_automation_matrix(self, id):
        return await self.get_item_with_related(id, 'automation_matrix')

    async def get_automation_boundary_brokers_with_automation_matrix(self):
        return await self.get_items_with_related('automation_matrix')

    async def load_automation_boundary_brokers_by_matrix(self, matrix):
        return await self.load_items(matrix=matrix)

    async def filter_automation_boundary_brokers_by_matrix(self, matrix):
        return await self.filter_items(matrix=matrix)

    async def load_automation_boundary_brokers_by_broker(self, broker):
        return await self.load_items(broker=broker)

    async def filter_automation_boundary_brokers_by_broker(self, broker):
        return await self.filter_items(broker=broker)

    async def load_automation_boundary_brokers_by_spark_source(self, spark_source):
        return await self.load_items(spark_source=spark_source)

    async def filter_automation_boundary_brokers_by_spark_source(self, spark_source):
        return await self.filter_items(spark_source=spark_source)

    async def load_automation_boundary_brokers_by_beacon_destination(self, beacon_destination):
        return await self.load_items(beacon_destination=beacon_destination)

    async def filter_automation_boundary_brokers_by_beacon_destination(self, beacon_destination):
        return await self.filter_items(beacon_destination=beacon_destination)

    async def load_automation_boundary_brokers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_automation_boundary_broker_ids(self):
        return self.active_item_ids



class AutomationBoundaryBrokerManager(AutomationBoundaryBrokerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AutomationBoundaryBrokerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

automation_boundary_broker_manager_instance = AutomationBoundaryBrokerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import BrokerValue
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class BrokerValueDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, broker_value_item):
        '''Override the base initialization method.'''
        self.id = str(broker_value_item.id)
        await self._process_core_data(broker_value_item)
        await self._process_metadata(broker_value_item)
        await self._initial_validation(broker_value_item)
        self.initialized = True

    async def _process_core_data(self, broker_value_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, broker_value_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, broker_value_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[BrokerValueDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class BrokerValueBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or BrokerValueDTO
        super().__init__(BrokerValue, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, broker_value):
        pass

    async def create_broker_value(self, **data):
        return await self.create_item(**data)

    async def delete_broker_value(self, id):
        return await self.delete_item(id)

    async def get_broker_value_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_broker_value_by_id(self, id):
        return await self.load_by_id(id)

    async def load_broker_value(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_broker_value(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_broker_values(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_broker_values(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_broker_value_with_data_broker(self, id):
        return await self.get_item_with_related(id, 'data_broker')

    async def get_broker_values_with_data_broker(self):
        return await self.get_items_with_related('data_broker')

    async def load_broker_values_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_broker_values_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_broker_values_by_data_broker(self, data_broker):
        return await self.load_items(data_broker=data_broker)

    async def filter_broker_values_by_data_broker(self, data_broker):
        return await self.filter_items(data_broker=data_broker)

    async def load_broker_values_by_tags(self, tags):
        return await self.load_items(tags=tags)

    async def filter_broker_values_by_tags(self, tags):
        return await self.filter_items(tags=tags)

    async def load_broker_values_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_broker_value_ids(self):
        return self.active_item_ids



class BrokerValueManager(BrokerValueBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BrokerValueManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

broker_value_manager_instance = BrokerValueManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import BucketStructures
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class BucketStructuresDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, bucket_structures_item):
        '''Override the base initialization method.'''
        self.id = str(bucket_structures_item.id)
        await self._process_core_data(bucket_structures_item)
        await self._process_metadata(bucket_structures_item)
        await self._initial_validation(bucket_structures_item)
        self.initialized = True

    async def _process_core_data(self, bucket_structures_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, bucket_structures_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, bucket_structures_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[BucketStructuresDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class BucketStructuresBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or BucketStructuresDTO
        super().__init__(BucketStructures, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, bucket_structures):
        pass

    async def create_bucket_structures(self, **data):
        return await self.create_item(**data)

    async def delete_bucket_structures(self, id):
        return await self.delete_item(id)

    async def get_bucket_structures_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_bucket_structures_by_id(self, id):
        return await self.load_by_id(id)

    async def load_bucket_structures(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_bucket_structures(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_bucket_structure(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_bucket_structure(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_bucket_structure_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_bucket_structures_ids(self):
        return self.active_item_ids



class BucketStructuresManager(BucketStructuresBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BucketStructuresManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

bucket_structures_manager_instance = BucketStructuresManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import BucketTreeStructures
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class BucketTreeStructuresDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, bucket_tree_structures_item):
        '''Override the base initialization method.'''
        self.id = str(bucket_tree_structures_item.id)
        await self._process_core_data(bucket_tree_structures_item)
        await self._process_metadata(bucket_tree_structures_item)
        await self._initial_validation(bucket_tree_structures_item)
        self.initialized = True

    async def _process_core_data(self, bucket_tree_structures_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, bucket_tree_structures_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, bucket_tree_structures_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[BucketTreeStructuresDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class BucketTreeStructuresBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or BucketTreeStructuresDTO
        super().__init__(BucketTreeStructures, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, bucket_tree_structures):
        pass

    async def create_bucket_tree_structures(self, **data):
        return await self.create_item(**data)

    async def delete_bucket_tree_structures(self, id):
        return await self.delete_item(id)

    async def get_bucket_tree_structures_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_bucket_tree_structures_by_id(self, id):
        return await self.load_by_id(id)

    async def load_bucket_tree_structures(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_bucket_tree_structures(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_bucket_tree_structure(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_bucket_tree_structure(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_bucket_tree_structure_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_bucket_tree_structures_ids(self):
        return self.active_item_ids



class BucketTreeStructuresManager(BucketTreeStructuresBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BucketTreeStructuresManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

bucket_tree_structures_manager_instance = BucketTreeStructuresManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Emails
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class EmailsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, emails_item):
        '''Override the base initialization method.'''
        self.id = str(emails_item.id)
        await self._process_core_data(emails_item)
        await self._process_metadata(emails_item)
        await self._initial_validation(emails_item)
        self.initialized = True

    async def _process_core_data(self, emails_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, emails_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, emails_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[EmailsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class EmailsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or EmailsDTO
        super().__init__(Emails, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, emails):
        pass

    async def create_emails(self, **data):
        return await self.create_item(**data)

    async def delete_emails(self, id):
        return await self.delete_item(id)

    async def get_emails_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_emails_by_id(self, id):
        return await self.load_by_id(id)

    async def load_emails(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_emails(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_email(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_email(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_email_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_emails_ids(self):
        return self.active_item_ids



class EmailsManager(EmailsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmailsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

emails_manager_instance = EmailsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Extractor
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ExtractorDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, extractor_item):
        '''Override the base initialization method.'''
        self.id = str(extractor_item.id)
        await self._process_core_data(extractor_item)
        await self._process_metadata(extractor_item)
        await self._initial_validation(extractor_item)
        self.initialized = True

    async def _process_core_data(self, extractor_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, extractor_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, extractor_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ExtractorDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ExtractorBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ExtractorDTO
        super().__init__(Extractor, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, extractor):
        pass

    async def create_extractor(self, **data):
        return await self.create_item(**data)

    async def delete_extractor(self, id):
        return await self.delete_item(id)

    async def get_extractor_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_extractor_by_id(self, id):
        return await self.load_by_id(id)

    async def load_extractor(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_extractor(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_extractors(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_extractors(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_extractors_by_output_type(self, output_type):
        return await self.load_items(output_type=output_type)

    async def filter_extractors_by_output_type(self, output_type):
        return await self.filter_items(output_type=output_type)

    async def load_extractors_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_extractor_ids(self):
        return self.active_item_ids



class ExtractorManager(ExtractorBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ExtractorManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

extractor_manager_instance = ExtractorManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FileStructure
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FileStructureDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, file_structure_item):
        '''Override the base initialization method.'''
        self.id = str(file_structure_item.id)
        await self._process_core_data(file_structure_item)
        await self._process_metadata(file_structure_item)
        await self._initial_validation(file_structure_item)
        self.initialized = True

    async def _process_core_data(self, file_structure_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, file_structure_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, file_structure_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FileStructureDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FileStructureBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FileStructureDTO
        super().__init__(FileStructure, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, file_structure):
        pass

    async def create_file_structure(self, **data):
        return await self.create_item(**data)

    async def delete_file_structure(self, id):
        return await self.delete_item(id)

    async def get_file_structure_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_file_structure_by_id(self, id):
        return await self.load_by_id(id)

    async def load_file_structure(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_file_structure(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_file_structures(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_file_structures(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_file_structures_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_file_structure_ids(self):
        return self.active_item_ids



class FileStructureManager(FileStructureBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FileStructureManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

file_structure_manager_instance = FileStructureManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FlashcardHistory
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FlashcardHistoryDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, flashcard_history_item):
        '''Override the base initialization method.'''
        self.id = str(flashcard_history_item.id)
        await self._process_core_data(flashcard_history_item)
        await self._process_metadata(flashcard_history_item)
        await self._initial_validation(flashcard_history_item)
        self.initialized = True

    async def _process_core_data(self, flashcard_history_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, flashcard_history_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, flashcard_history_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FlashcardHistoryDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FlashcardHistoryBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FlashcardHistoryDTO
        super().__init__(FlashcardHistory, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_history):
        pass

    async def create_flashcard_history(self, **data):
        return await self.create_item(**data)

    async def delete_flashcard_history(self, id):
        return await self.delete_item(id)

    async def get_flashcard_history_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_flashcard_history_by_id(self, id):
        return await self.load_by_id(id)

    async def load_flashcard_history(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_flashcard_history(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_flashcard_histories(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_flashcard_histories(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_flashcard_history_with_flashcard_data(self, id):
        return await self.get_item_with_related(id, 'flashcard_data')

    async def get_flashcard_histories_with_flashcard_data(self):
        return await self.get_items_with_related('flashcard_data')

    async def load_flashcard_histories_by_flashcard_id(self, flashcard_id):
        return await self.load_items(flashcard_id=flashcard_id)

    async def filter_flashcard_histories_by_flashcard_id(self, flashcard_id):
        return await self.filter_items(flashcard_id=flashcard_id)

    async def load_flashcard_histories_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_flashcard_histories_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_flashcard_histories_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_flashcard_history_ids(self):
        return self.active_item_ids



class FlashcardHistoryManager(FlashcardHistoryBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlashcardHistoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

flashcard_history_manager_instance = FlashcardHistoryManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FlashcardImages
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FlashcardImagesDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, flashcard_images_item):
        '''Override the base initialization method.'''
        self.id = str(flashcard_images_item.id)
        await self._process_core_data(flashcard_images_item)
        await self._process_metadata(flashcard_images_item)
        await self._initial_validation(flashcard_images_item)
        self.initialized = True

    async def _process_core_data(self, flashcard_images_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, flashcard_images_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, flashcard_images_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FlashcardImagesDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FlashcardImagesBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FlashcardImagesDTO
        super().__init__(FlashcardImages, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_images):
        pass

    async def create_flashcard_images(self, **data):
        return await self.create_item(**data)

    async def delete_flashcard_images(self, id):
        return await self.delete_item(id)

    async def get_flashcard_images_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_flashcard_images_by_id(self, id):
        return await self.load_by_id(id)

    async def load_flashcard_images(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_flashcard_images(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_flashcard_image(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_flashcard_image(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_flashcard_images_with_flashcard_data(self, id):
        return await self.get_item_with_related(id, 'flashcard_data')

    async def get_flashcard_image_with_flashcard_data(self):
        return await self.get_items_with_related('flashcard_data')

    async def load_flashcard_image_by_flashcard_id(self, flashcard_id):
        return await self.load_items(flashcard_id=flashcard_id)

    async def filter_flashcard_image_by_flashcard_id(self, flashcard_id):
        return await self.filter_items(flashcard_id=flashcard_id)

    async def load_flashcard_image_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_flashcard_images_ids(self):
        return self.active_item_ids



class FlashcardImagesManager(FlashcardImagesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlashcardImagesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

flashcard_images_manager_instance = FlashcardImagesManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FlashcardSetRelations
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FlashcardSetRelationsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, flashcard_set_relations_item):
        '''Override the base initialization method.'''
        self.id = str(flashcard_set_relations_item.id)
        await self._process_core_data(flashcard_set_relations_item)
        await self._process_metadata(flashcard_set_relations_item)
        await self._initial_validation(flashcard_set_relations_item)
        self.initialized = True

    async def _process_core_data(self, flashcard_set_relations_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, flashcard_set_relations_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, flashcard_set_relations_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FlashcardSetRelationsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FlashcardSetRelationsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FlashcardSetRelationsDTO
        super().__init__(FlashcardSetRelations, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, flashcard_set_relations):
        pass

    async def create_flashcard_set_relations(self, **data):
        return await self.create_item(**data)

    async def delete_flashcard_set_relations(self, id):
        return await self.delete_item(id)

    async def get_flashcard_set_relations_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_flashcard_set_relations_by_id(self, id):
        return await self.load_by_id(id)

    async def load_flashcard_set_relations(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_flashcard_set_relations(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_flashcard_set_relation(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_flashcard_set_relation(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_flashcard_set_relations_with_flashcard_data(self, id):
        return await self.get_item_with_related(id, 'flashcard_data')

    async def get_flashcard_set_relation_with_flashcard_data(self):
        return await self.get_items_with_related('flashcard_data')

    async def get_flashcard_set_relations_with_flashcard_sets(self, id):
        return await self.get_item_with_related(id, 'flashcard_sets')

    async def get_flashcard_set_relation_with_flashcard_sets(self):
        return await self.get_items_with_related('flashcard_sets')

    async def load_flashcard_set_relation_by_flashcard_id(self, flashcard_id):
        return await self.load_items(flashcard_id=flashcard_id)

    async def filter_flashcard_set_relation_by_flashcard_id(self, flashcard_id):
        return await self.filter_items(flashcard_id=flashcard_id)

    async def load_flashcard_set_relation_by_set_id(self, set_id):
        return await self.load_items(set_id=set_id)

    async def filter_flashcard_set_relation_by_set_id(self, set_id):
        return await self.filter_items(set_id=set_id)

    async def load_flashcard_set_relation_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_flashcard_set_relations_ids(self):
        return self.active_item_ids



class FlashcardSetRelationsManager(FlashcardSetRelationsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlashcardSetRelationsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

flashcard_set_relations_manager_instance = FlashcardSetRelationsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import FullSpectrumPositions
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class FullSpectrumPositionsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, full_spectrum_positions_item):
        '''Override the base initialization method.'''
        self.id = str(full_spectrum_positions_item.id)
        await self._process_core_data(full_spectrum_positions_item)
        await self._process_metadata(full_spectrum_positions_item)
        await self._initial_validation(full_spectrum_positions_item)
        self.initialized = True

    async def _process_core_data(self, full_spectrum_positions_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, full_spectrum_positions_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, full_spectrum_positions_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[FullSpectrumPositionsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class FullSpectrumPositionsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or FullSpectrumPositionsDTO
        super().__init__(FullSpectrumPositions, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, full_spectrum_positions):
        pass

    async def create_full_spectrum_positions(self, **data):
        return await self.create_item(**data)

    async def delete_full_spectrum_positions(self, id):
        return await self.delete_item(id)

    async def get_full_spectrum_positions_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_full_spectrum_positions_by_id(self, id):
        return await self.load_by_id(id)

    async def load_full_spectrum_positions(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_full_spectrum_positions(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_full_spectrum_position(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_full_spectrum_position(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_full_spectrum_position_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_full_spectrum_positions_ids(self):
        return self.active_item_ids



class FullSpectrumPositionsManager(FullSpectrumPositionsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FullSpectrumPositionsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

full_spectrum_positions_manager_instance = FullSpectrumPositionsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Message
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class MessageDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, message_item):
        '''Override the base initialization method.'''
        self.id = str(message_item.id)
        await self._process_core_data(message_item)
        await self._process_metadata(message_item)
        await self._initial_validation(message_item)
        self.initialized = True

    async def _process_core_data(self, message_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, message_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, message_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[MessageDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class MessageBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or MessageDTO
        super().__init__(Message, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message):
        pass

    async def create_message(self, **data):
        return await self.create_item(**data)

    async def delete_message(self, id):
        return await self.delete_item(id)

    async def get_message_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_message_by_id(self, id):
        return await self.load_by_id(id)

    async def load_message(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_message(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_messages(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_messages(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_message_with_conversation(self, id):
        return await self.get_item_with_related(id, 'conversation')

    async def get_messages_with_conversation(self):
        return await self.get_items_with_related('conversation')

    async def load_messages_by_conversation_id(self, conversation_id):
        return await self.load_items(conversation_id=conversation_id)

    async def filter_messages_by_conversation_id(self, conversation_id):
        return await self.filter_items(conversation_id=conversation_id)

    async def load_messages_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_messages_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_messages_by_type(self, type):
        return await self.load_items(type=type)

    async def filter_messages_by_type(self, type):
        return await self.filter_items(type=type)

    async def load_messages_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_messages_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_messages_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_message_ids(self):
        return self.active_item_ids



class MessageManager(MessageBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MessageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

message_manager_instance = MessageManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import MessageBroker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class MessageBrokerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, message_broker_item):
        '''Override the base initialization method.'''
        self.id = str(message_broker_item.id)
        await self._process_core_data(message_broker_item)
        await self._process_metadata(message_broker_item)
        await self._initial_validation(message_broker_item)
        self.initialized = True

    async def _process_core_data(self, message_broker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, message_broker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, message_broker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[MessageBrokerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class MessageBrokerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or MessageBrokerDTO
        super().__init__(MessageBroker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, message_broker):
        pass

    async def create_message_broker(self, **data):
        return await self.create_item(**data)

    async def delete_message_broker(self, id):
        return await self.delete_item(id)

    async def get_message_broker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_message_broker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_message_broker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_message_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_message_brokers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_message_brokers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_message_broker_with_data_broker(self, id):
        return await self.get_item_with_related(id, 'data_broker')

    async def get_message_brokers_with_data_broker(self):
        return await self.get_items_with_related('data_broker')

    async def get_message_broker_with_data_input_component(self, id):
        return await self.get_item_with_related(id, 'data_input_component')

    async def get_message_brokers_with_data_input_component(self):
        return await self.get_items_with_related('data_input_component')

    async def get_message_broker_with_message_template(self, id):
        return await self.get_item_with_related(id, 'message_template')

    async def get_message_brokers_with_message_template(self):
        return await self.get_items_with_related('message_template')

    async def load_message_brokers_by_message_id(self, message_id):
        return await self.load_items(message_id=message_id)

    async def filter_message_brokers_by_message_id(self, message_id):
        return await self.filter_items(message_id=message_id)

    async def load_message_brokers_by_broker_id(self, broker_id):
        return await self.load_items(broker_id=broker_id)

    async def filter_message_brokers_by_broker_id(self, broker_id):
        return await self.filter_items(broker_id=broker_id)

    async def load_message_brokers_by_default_component(self, default_component):
        return await self.load_items(default_component=default_component)

    async def filter_message_brokers_by_default_component(self, default_component):
        return await self.filter_items(default_component=default_component)

    async def load_message_brokers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_message_broker_ids(self):
        return self.active_item_ids



class MessageBrokerManager(MessageBrokerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MessageBrokerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

message_broker_manager_instance = MessageBrokerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import OrganizationInvitations
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class OrganizationInvitationsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, organization_invitations_item):
        '''Override the base initialization method.'''
        self.id = str(organization_invitations_item.id)
        await self._process_core_data(organization_invitations_item)
        await self._process_metadata(organization_invitations_item)
        await self._initial_validation(organization_invitations_item)
        self.initialized = True

    async def _process_core_data(self, organization_invitations_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, organization_invitations_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, organization_invitations_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[OrganizationInvitationsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class OrganizationInvitationsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or OrganizationInvitationsDTO
        super().__init__(OrganizationInvitations, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organization_invitations):
        pass

    async def create_organization_invitations(self, **data):
        return await self.create_item(**data)

    async def delete_organization_invitations(self, id):
        return await self.delete_item(id)

    async def get_organization_invitations_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_organization_invitations_by_id(self, id):
        return await self.load_by_id(id)

    async def load_organization_invitations(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_organization_invitations(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_organization_invitation(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_organization_invitation(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_organization_invitations_with_organizations(self, id):
        return await self.get_item_with_related(id, 'organizations')

    async def get_organization_invitation_with_organizations(self):
        return await self.get_items_with_related('organizations')

    async def load_organization_invitation_by_organization_id(self, organization_id):
        return await self.load_items(organization_id=organization_id)

    async def filter_organization_invitation_by_organization_id(self, organization_id):
        return await self.filter_items(organization_id=organization_id)

    async def load_organization_invitation_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_organization_invitation_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_organization_invitation_by_invited_by(self, invited_by):
        return await self.load_items(invited_by=invited_by)

    async def filter_organization_invitation_by_invited_by(self, invited_by):
        return await self.filter_items(invited_by=invited_by)

    async def load_organization_invitation_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_organization_invitations_ids(self):
        return self.active_item_ids



class OrganizationInvitationsManager(OrganizationInvitationsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OrganizationInvitationsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

organization_invitations_manager_instance = OrganizationInvitationsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import OrganizationMembers
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class OrganizationMembersDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, organization_members_item):
        '''Override the base initialization method.'''
        self.id = str(organization_members_item.id)
        await self._process_core_data(organization_members_item)
        await self._process_metadata(organization_members_item)
        await self._initial_validation(organization_members_item)
        self.initialized = True

    async def _process_core_data(self, organization_members_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, organization_members_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, organization_members_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[OrganizationMembersDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class OrganizationMembersBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or OrganizationMembersDTO
        super().__init__(OrganizationMembers, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, organization_members):
        pass

    async def create_organization_members(self, **data):
        return await self.create_item(**data)

    async def delete_organization_members(self, id):
        return await self.delete_item(id)

    async def get_organization_members_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_organization_members_by_id(self, id):
        return await self.load_by_id(id)

    async def load_organization_members(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_organization_members(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_organization_member(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_organization_member(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_organization_members_with_organizations(self, id):
        return await self.get_item_with_related(id, 'organizations')

    async def get_organization_member_with_organizations(self):
        return await self.get_items_with_related('organizations')

    async def load_organization_member_by_organization_id(self, organization_id):
        return await self.load_items(organization_id=organization_id)

    async def filter_organization_member_by_organization_id(self, organization_id):
        return await self.filter_items(organization_id=organization_id)

    async def load_organization_member_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_organization_member_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_organization_member_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_organization_member_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_organization_member_by_invited_by(self, invited_by):
        return await self.load_items(invited_by=invited_by)

    async def filter_organization_member_by_invited_by(self, invited_by):
        return await self.filter_items(invited_by=invited_by)

    async def load_organization_member_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_organization_members_ids(self):
        return self.active_item_ids



class OrganizationMembersManager(OrganizationMembersBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OrganizationMembersManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

organization_members_manager_instance = OrganizationMembersManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import Permissions
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class PermissionsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, permissions_item):
        '''Override the base initialization method.'''
        self.id = str(permissions_item.id)
        await self._process_core_data(permissions_item)
        await self._process_metadata(permissions_item)
        await self._initial_validation(permissions_item)
        self.initialized = True

    async def _process_core_data(self, permissions_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, permissions_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, permissions_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[PermissionsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class PermissionsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or PermissionsDTO
        super().__init__(Permissions, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, permissions):
        pass

    async def create_permissions(self, **data):
        return await self.create_item(**data)

    async def delete_permissions(self, id):
        return await self.delete_item(id)

    async def get_permissions_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_permissions_by_id(self, id):
        return await self.load_by_id(id)

    async def load_permissions(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_permissions(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_permission(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_permission(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_permissions_with_organizations(self, id):
        return await self.get_item_with_related(id, 'organizations')

    async def get_permission_with_organizations(self):
        return await self.get_items_with_related('organizations')

    async def load_permission_by_resource_type(self, resource_type):
        return await self.load_items(resource_type=resource_type)

    async def filter_permission_by_resource_type(self, resource_type):
        return await self.filter_items(resource_type=resource_type)

    async def load_permission_by_granted_to_user_id(self, granted_to_user_id):
        return await self.load_items(granted_to_user_id=granted_to_user_id)

    async def filter_permission_by_granted_to_user_id(self, granted_to_user_id):
        return await self.filter_items(granted_to_user_id=granted_to_user_id)

    async def load_permission_by_granted_to_organization_id(self, granted_to_organization_id):
        return await self.load_items(granted_to_organization_id=granted_to_organization_id)

    async def filter_permission_by_granted_to_organization_id(self, granted_to_organization_id):
        return await self.filter_items(granted_to_organization_id=granted_to_organization_id)

    async def load_permission_by_permission_level(self, permission_level):
        return await self.load_items(permission_level=permission_level)

    async def filter_permission_by_permission_level(self, permission_level):
        return await self.filter_items(permission_level=permission_level)

    async def load_permission_by_created_by(self, created_by):
        return await self.load_items(created_by=created_by)

    async def filter_permission_by_created_by(self, created_by):
        return await self.filter_items(created_by=created_by)

    async def load_permission_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_permissions_ids(self):
        return self.active_item_ids



class PermissionsManager(PermissionsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PermissionsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

permissions_manager_instance = PermissionsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ProjectMembers
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ProjectMembersDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, project_members_item):
        '''Override the base initialization method.'''
        self.id = str(project_members_item.id)
        await self._process_core_data(project_members_item)
        await self._process_metadata(project_members_item)
        await self._initial_validation(project_members_item)
        self.initialized = True

    async def _process_core_data(self, project_members_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, project_members_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, project_members_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ProjectMembersDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ProjectMembersBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ProjectMembersDTO
        super().__init__(ProjectMembers, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, project_members):
        pass

    async def create_project_members(self, **data):
        return await self.create_item(**data)

    async def delete_project_members(self, id):
        return await self.delete_item(id)

    async def get_project_members_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_project_members_by_id(self, id):
        return await self.load_by_id(id)

    async def load_project_members(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_project_members(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_project_member(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_project_member(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_project_members_with_projects(self, id):
        return await self.get_item_with_related(id, 'projects')

    async def get_project_member_with_projects(self):
        return await self.get_items_with_related('projects')

    async def load_project_member_by_project_id(self, project_id):
        return await self.load_items(project_id=project_id)

    async def filter_project_member_by_project_id(self, project_id):
        return await self.filter_items(project_id=project_id)

    async def load_project_member_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_project_member_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_project_member_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_project_members_ids(self):
        return self.active_item_ids



class ProjectMembersManager(ProjectMembersBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProjectMembersManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

project_members_manager_instance = ProjectMembersManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeBroker
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeBrokerDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_broker_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_broker_item.id)
        await self._process_core_data(recipe_broker_item)
        await self._process_metadata(recipe_broker_item)
        await self._initial_validation(recipe_broker_item)
        self.initialized = True

    async def _process_core_data(self, recipe_broker_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_broker_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_broker_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeBrokerDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeBrokerBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeBrokerDTO
        super().__init__(RecipeBroker, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_broker):
        pass

    async def create_recipe_broker(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_broker(self, id):
        return await self.delete_item(id)

    async def get_recipe_broker_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_broker_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_broker(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_brokers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_brokers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_broker_with_broker(self, id):
        return await self.get_item_with_related(id, 'broker')

    async def get_recipe_brokers_with_broker(self):
        return await self.get_items_with_related('broker')

    async def get_recipe_broker_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_brokers_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_brokers_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_brokers_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_brokers_by_broker(self, broker):
        return await self.load_items(broker=broker)

    async def filter_recipe_brokers_by_broker(self, broker):
        return await self.filter_items(broker=broker)

    async def load_recipe_brokers_by_broker_role(self, broker_role):
        return await self.load_items(broker_role=broker_role)

    async def filter_recipe_brokers_by_broker_role(self, broker_role):
        return await self.filter_items(broker_role=broker_role)

    async def load_recipe_brokers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_broker_ids(self):
        return self.active_item_ids



class RecipeBrokerManager(RecipeBrokerBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeBrokerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_broker_manager_instance = RecipeBrokerManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeDisplay
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeDisplayDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_display_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_display_item.id)
        await self._process_core_data(recipe_display_item)
        await self._process_metadata(recipe_display_item)
        await self._initial_validation(recipe_display_item)
        self.initialized = True

    async def _process_core_data(self, recipe_display_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_display_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_display_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeDisplayDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeDisplayBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeDisplayDTO
        super().__init__(RecipeDisplay, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_display):
        pass

    async def create_recipe_display(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_display(self, id):
        return await self.delete_item(id)

    async def get_recipe_display_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_display_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_display(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_display(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_displays(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_displays(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_display_with_display_option(self, id):
        return await self.get_item_with_related(id, 'display_option')

    async def get_recipe_displays_with_display_option(self):
        return await self.get_items_with_related('display_option')

    async def get_recipe_display_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_displays_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_displays_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_displays_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_displays_by_display(self, display):
        return await self.load_items(display=display)

    async def filter_recipe_displays_by_display(self, display):
        return await self.filter_items(display=display)

    async def load_recipe_displays_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_display_ids(self):
        return self.active_item_ids



class RecipeDisplayManager(RecipeDisplayBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeDisplayManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_display_manager_instance = RecipeDisplayManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeFunction
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeFunctionDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_function_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_function_item.id)
        await self._process_core_data(recipe_function_item)
        await self._process_metadata(recipe_function_item)
        await self._initial_validation(recipe_function_item)
        self.initialized = True

    async def _process_core_data(self, recipe_function_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_function_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_function_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeFunctionDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeFunctionBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeFunctionDTO
        super().__init__(RecipeFunction, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_function):
        pass

    async def create_recipe_function(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_function(self, id):
        return await self.delete_item(id)

    async def get_recipe_function_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_function_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_function(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_function(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_functions(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_functions(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_function_with_system_function(self, id):
        return await self.get_item_with_related(id, 'system_function')

    async def get_recipe_functions_with_system_function(self):
        return await self.get_items_with_related('system_function')

    async def get_recipe_function_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_functions_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_functions_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_functions_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_functions_by_function(self, function):
        return await self.load_items(function=function)

    async def filter_recipe_functions_by_function(self, function):
        return await self.filter_items(function=function)

    async def load_recipe_functions_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_recipe_functions_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_recipe_functions_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_function_ids(self):
        return self.active_item_ids



class RecipeFunctionManager(RecipeFunctionBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeFunctionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_function_manager_instance = RecipeFunctionManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeMessage
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeMessageDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_message_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_message_item.id)
        await self._process_core_data(recipe_message_item)
        await self._process_metadata(recipe_message_item)
        await self._initial_validation(recipe_message_item)
        self.initialized = True

    async def _process_core_data(self, recipe_message_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_message_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_message_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeMessageDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeMessageBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeMessageDTO
        super().__init__(RecipeMessage, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_message):
        pass

    async def create_recipe_message(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_message(self, id):
        return await self.delete_item(id)

    async def get_recipe_message_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_message_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_message(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_message(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_messages(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_messages(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_message_with_message_template(self, id):
        return await self.get_item_with_related(id, 'message_template')

    async def get_recipe_messages_with_message_template(self):
        return await self.get_items_with_related('message_template')

    async def get_recipe_message_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_messages_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_messages_by_message_id(self, message_id):
        return await self.load_items(message_id=message_id)

    async def filter_recipe_messages_by_message_id(self, message_id):
        return await self.filter_items(message_id=message_id)

    async def load_recipe_messages_by_recipe_id(self, recipe_id):
        return await self.load_items(recipe_id=recipe_id)

    async def filter_recipe_messages_by_recipe_id(self, recipe_id):
        return await self.filter_items(recipe_id=recipe_id)

    async def load_recipe_messages_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_message_ids(self):
        return self.active_item_ids



class RecipeMessageManager(RecipeMessageBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeMessageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_message_manager_instance = RecipeMessageManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeMessageReorderQueue
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeMessageReorderQueueDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_message_reorder_queue_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_message_reorder_queue_item.id)
        await self._process_core_data(recipe_message_reorder_queue_item)
        await self._process_metadata(recipe_message_reorder_queue_item)
        await self._initial_validation(recipe_message_reorder_queue_item)
        self.initialized = True

    async def _process_core_data(self, recipe_message_reorder_queue_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_message_reorder_queue_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_message_reorder_queue_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeMessageReorderQueueDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeMessageReorderQueueBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeMessageReorderQueueDTO
        super().__init__(RecipeMessageReorderQueue, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_message_reorder_queue):
        pass

    async def create_recipe_message_reorder_queue(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_message_reorder_queue(self, id):
        return await self.delete_item(id)

    async def get_recipe_message_reorder_queue_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_message_reorder_queue_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_message_reorder_queue(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_message_reorder_queue(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_message_reorder_queues(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_message_reorder_queues(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_recipe_message_reorder_queues_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_message_reorder_queue_ids(self):
        return self.active_item_ids



class RecipeMessageReorderQueueManager(RecipeMessageReorderQueueBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeMessageReorderQueueManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_message_reorder_queue_manager_instance = RecipeMessageReorderQueueManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeModel
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeModelDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_model_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_model_item.id)
        await self._process_core_data(recipe_model_item)
        await self._process_metadata(recipe_model_item)
        await self._initial_validation(recipe_model_item)
        self.initialized = True

    async def _process_core_data(self, recipe_model_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_model_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_model_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeModelDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeModelBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeModelDTO
        super().__init__(RecipeModel, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_model):
        pass

    async def create_recipe_model(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_model(self, id):
        return await self.delete_item(id)

    async def get_recipe_model_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_model_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_model(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_model(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_models(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_models(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_model_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_recipe_models_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def get_recipe_model_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_models_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_models_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_models_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_models_by_ai_model(self, ai_model):
        return await self.load_items(ai_model=ai_model)

    async def filter_recipe_models_by_ai_model(self, ai_model):
        return await self.filter_items(ai_model=ai_model)

    async def load_recipe_models_by_role(self, role):
        return await self.load_items(role=role)

    async def filter_recipe_models_by_role(self, role):
        return await self.filter_items(role=role)

    async def load_recipe_models_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_model_ids(self):
        return self.active_item_ids



class RecipeModelManager(RecipeModelBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_model_manager_instance = RecipeModelManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeProcessor
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeProcessorDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_processor_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_processor_item.id)
        await self._process_core_data(recipe_processor_item)
        await self._process_metadata(recipe_processor_item)
        await self._initial_validation(recipe_processor_item)
        self.initialized = True

    async def _process_core_data(self, recipe_processor_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_processor_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_processor_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeProcessorDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeProcessorBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeProcessorDTO
        super().__init__(RecipeProcessor, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_processor):
        pass

    async def create_recipe_processor(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_processor(self, id):
        return await self.delete_item(id)

    async def get_recipe_processor_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_processor_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_processor(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_processor(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_processors(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_processors(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_processor_with_processor(self, id):
        return await self.get_item_with_related(id, 'processor')

    async def get_recipe_processors_with_processor(self):
        return await self.get_items_with_related('processor')

    async def get_recipe_processor_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_processors_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def load_recipe_processors_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_processors_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_processors_by_processor(self, processor):
        return await self.load_items(processor=processor)

    async def filter_recipe_processors_by_processor(self, processor):
        return await self.filter_items(processor=processor)

    async def load_recipe_processors_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_processor_ids(self):
        return self.active_item_ids



class RecipeProcessorManager(RecipeProcessorBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeProcessorManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_processor_manager_instance = RecipeProcessorManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import RecipeTool
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class RecipeToolDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, recipe_tool_item):
        '''Override the base initialization method.'''
        self.id = str(recipe_tool_item.id)
        await self._process_core_data(recipe_tool_item)
        await self._process_metadata(recipe_tool_item)
        await self._initial_validation(recipe_tool_item)
        self.initialized = True

    async def _process_core_data(self, recipe_tool_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, recipe_tool_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, recipe_tool_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[RecipeToolDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class RecipeToolBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or RecipeToolDTO
        super().__init__(RecipeTool, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, recipe_tool):
        pass

    async def create_recipe_tool(self, **data):
        return await self.create_item(**data)

    async def delete_recipe_tool(self, id):
        return await self.delete_item(id)

    async def get_recipe_tool_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_recipe_tool_by_id(self, id):
        return await self.load_by_id(id)

    async def load_recipe_tool(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_recipe_tool(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_recipe_tools(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_recipe_tools(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_recipe_tool_with_recipe(self, id):
        return await self.get_item_with_related(id, 'recipe')

    async def get_recipe_tools_with_recipe(self):
        return await self.get_items_with_related('recipe')

    async def get_recipe_tool_with_tool(self, id):
        return await self.get_item_with_related(id, 'tool')

    async def get_recipe_tools_with_tool(self):
        return await self.get_items_with_related('tool')

    async def load_recipe_tools_by_recipe(self, recipe):
        return await self.load_items(recipe=recipe)

    async def filter_recipe_tools_by_recipe(self, recipe):
        return await self.filter_items(recipe=recipe)

    async def load_recipe_tools_by_tool(self, tool):
        return await self.load_items(tool=tool)

    async def filter_recipe_tools_by_tool(self, tool):
        return await self.filter_items(tool=tool)

    async def load_recipe_tools_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_recipe_tool_ids(self):
        return self.active_item_ids



class RecipeToolManager(RecipeToolBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RecipeToolManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

recipe_tool_manager_instance = RecipeToolManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomainDisallowedNotes
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainDisallowedNotesDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_disallowed_notes_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_disallowed_notes_item.id)
        await self._process_core_data(scrape_domain_disallowed_notes_item)
        await self._process_metadata(scrape_domain_disallowed_notes_item)
        await self._initial_validation(scrape_domain_disallowed_notes_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_disallowed_notes_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_disallowed_notes_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_disallowed_notes_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainDisallowedNotesDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainDisallowedNotesBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainDisallowedNotesDTO
        super().__init__(ScrapeDomainDisallowedNotes, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_disallowed_notes):
        pass

    async def create_scrape_domain_disallowed_notes(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain_disallowed_notes(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_disallowed_notes_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_disallowed_notes_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain_disallowed_notes(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain_disallowed_notes(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domain_disallowed_note(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domain_disallowed_note(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_disallowed_notes_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_domain_disallowed_note_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_domain_disallowed_note_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_domain_disallowed_note_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_domain_disallowed_note_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_disallowed_notes_ids(self):
        return self.active_item_ids



class ScrapeDomainDisallowedNotesManager(ScrapeDomainDisallowedNotesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainDisallowedNotesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_disallowed_notes_manager_instance = ScrapeDomainDisallowedNotesManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomainNotes
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainNotesDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_notes_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_notes_item.id)
        await self._process_core_data(scrape_domain_notes_item)
        await self._process_metadata(scrape_domain_notes_item)
        await self._initial_validation(scrape_domain_notes_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_notes_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_notes_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_notes_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainNotesDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainNotesBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainNotesDTO
        super().__init__(ScrapeDomainNotes, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_notes):
        pass

    async def create_scrape_domain_notes(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain_notes(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_notes_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_notes_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain_notes(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain_notes(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domain_note(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domain_note(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_notes_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_domain_note_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_domain_note_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_domain_note_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_domain_note_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_notes_ids(self):
        return self.active_item_ids



class ScrapeDomainNotesManager(ScrapeDomainNotesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainNotesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_notes_manager_instance = ScrapeDomainNotesManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomainQuickScrapeSettings
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainQuickScrapeSettingsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_quick_scrape_settings_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_quick_scrape_settings_item.id)
        await self._process_core_data(scrape_domain_quick_scrape_settings_item)
        await self._process_metadata(scrape_domain_quick_scrape_settings_item)
        await self._initial_validation(scrape_domain_quick_scrape_settings_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_quick_scrape_settings_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_quick_scrape_settings_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_quick_scrape_settings_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainQuickScrapeSettingsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainQuickScrapeSettingsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainQuickScrapeSettingsDTO
        super().__init__(ScrapeDomainQuickScrapeSettings, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_quick_scrape_settings):
        pass

    async def create_scrape_domain_quick_scrape_settings(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain_quick_scrape_settings(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_quick_scrape_settings_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_quick_scrape_settings_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain_quick_scrape_settings(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain_quick_scrape_settings(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domain_quick_scrape_setting(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domain_quick_scrape_setting(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_quick_scrape_settings_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_domain_quick_scrape_setting_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_domain_quick_scrape_setting_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_domain_quick_scrape_setting_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_domain_quick_scrape_setting_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_quick_scrape_settings_ids(self):
        return self.active_item_ids



class ScrapeDomainQuickScrapeSettingsManager(ScrapeDomainQuickScrapeSettingsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainQuickScrapeSettingsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_quick_scrape_settings_manager_instance = ScrapeDomainQuickScrapeSettingsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomainRobotsTxt
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainRobotsTxtDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_robots_txt_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_robots_txt_item.id)
        await self._process_core_data(scrape_domain_robots_txt_item)
        await self._process_metadata(scrape_domain_robots_txt_item)
        await self._initial_validation(scrape_domain_robots_txt_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_robots_txt_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_robots_txt_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_robots_txt_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainRobotsTxtDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainRobotsTxtBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainRobotsTxtDTO
        super().__init__(ScrapeDomainRobotsTxt, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_robots_txt):
        pass

    async def create_scrape_domain_robots_txt(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain_robots_txt(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_robots_txt_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_robots_txt_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain_robots_txt(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain_robots_txt(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domain_robots_txts(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domain_robots_txts(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_robots_txt_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_domain_robots_txts_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_domain_robots_txts_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_domain_robots_txts_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_domain_robots_txts_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_robots_txt_ids(self):
        return self.active_item_ids



class ScrapeDomainRobotsTxtManager(ScrapeDomainRobotsTxtBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainRobotsTxtManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_robots_txt_manager_instance = ScrapeDomainRobotsTxtManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeDomainSitemap
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeDomainSitemapDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_domain_sitemap_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_domain_sitemap_item.id)
        await self._process_core_data(scrape_domain_sitemap_item)
        await self._process_metadata(scrape_domain_sitemap_item)
        await self._initial_validation(scrape_domain_sitemap_item)
        self.initialized = True

    async def _process_core_data(self, scrape_domain_sitemap_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_domain_sitemap_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_domain_sitemap_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeDomainSitemapDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeDomainSitemapBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeDomainSitemapDTO
        super().__init__(ScrapeDomainSitemap, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_domain_sitemap):
        pass

    async def create_scrape_domain_sitemap(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_domain_sitemap(self, id):
        return await self.delete_item(id)

    async def get_scrape_domain_sitemap_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_domain_sitemap_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_domain_sitemap(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_domain_sitemap(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_domain_sitemaps(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_domain_sitemaps(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_domain_sitemap_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_domain_sitemaps_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_domain_sitemaps_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_domain_sitemaps_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_domain_sitemaps_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_domain_sitemap_ids(self):
        return self.active_item_ids



class ScrapeDomainSitemapManager(ScrapeDomainSitemapBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeDomainSitemapManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_domain_sitemap_manager_instance = ScrapeDomainSitemapManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeOverrideValue
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeOverrideValueDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_override_value_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_override_value_item.id)
        await self._process_core_data(scrape_override_value_item)
        await self._process_metadata(scrape_override_value_item)
        await self._initial_validation(scrape_override_value_item)
        self.initialized = True

    async def _process_core_data(self, scrape_override_value_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_override_value_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_override_value_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeOverrideValueDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeOverrideValueBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeOverrideValueDTO
        super().__init__(ScrapeOverrideValue, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_override_value):
        pass

    async def create_scrape_override_value(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_override_value(self, id):
        return await self.delete_item(id)

    async def get_scrape_override_value_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_override_value_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_override_value(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_override_value(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_override_values(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_override_values(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_override_value_with_scrape_override(self, id):
        return await self.get_item_with_related(id, 'scrape_override')

    async def get_scrape_override_values_with_scrape_override(self):
        return await self.get_items_with_related('scrape_override')

    async def load_scrape_override_values_by_scrape_override_id(self, scrape_override_id):
        return await self.load_items(scrape_override_id=scrape_override_id)

    async def filter_scrape_override_values_by_scrape_override_id(self, scrape_override_id):
        return await self.filter_items(scrape_override_id=scrape_override_id)

    async def load_scrape_override_values_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_override_values_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_override_values_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_override_value_ids(self):
        return self.active_item_ids



class ScrapeOverrideValueManager(ScrapeOverrideValueBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeOverrideValueManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_override_value_manager_instance = ScrapeOverrideValueManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeParsedPage
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeParsedPageDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_parsed_page_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_parsed_page_item.id)
        await self._process_core_data(scrape_parsed_page_item)
        await self._process_metadata(scrape_parsed_page_item)
        await self._initial_validation(scrape_parsed_page_item)
        self.initialized = True

    async def _process_core_data(self, scrape_parsed_page_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_parsed_page_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_parsed_page_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeParsedPageDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeParsedPageBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeParsedPageDTO
        super().__init__(ScrapeParsedPage, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_parsed_page):
        pass

    async def create_scrape_parsed_page(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_parsed_page(self, id):
        return await self.delete_item(id)

    async def get_scrape_parsed_page_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_parsed_page_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_parsed_page(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_parsed_page(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_parsed_pages(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_parsed_pages(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_parsed_page_with_scrape_configuration(self, id):
        return await self.get_item_with_related(id, 'scrape_configuration')

    async def get_scrape_parsed_pages_with_scrape_configuration(self):
        return await self.get_items_with_related('scrape_configuration')

    async def get_scrape_parsed_page_with_scrape_cycle_run(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_run')

    async def get_scrape_parsed_pages_with_scrape_cycle_run(self):
        return await self.get_items_with_related('scrape_cycle_run')

    async def get_scrape_parsed_page_with_scrape_cycle_tracker(self, id):
        return await self.get_item_with_related(id, 'scrape_cycle_tracker')

    async def get_scrape_parsed_pages_with_scrape_cycle_tracker(self):
        return await self.get_items_with_related('scrape_cycle_tracker')

    async def get_scrape_parsed_page_with_scrape_path_pattern_cache_policy(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_cache_policy')

    async def get_scrape_parsed_pages_with_scrape_path_pattern_cache_policy(self):
        return await self.get_items_with_related('scrape_path_pattern_cache_policy')

    async def get_scrape_parsed_page_with_scrape_path_pattern_override(self, id):
        return await self.get_item_with_related(id, 'scrape_path_pattern_override')

    async def get_scrape_parsed_pages_with_scrape_path_pattern_override(self):
        return await self.get_items_with_related('scrape_path_pattern_override')

    async def get_scrape_parsed_page_with_scrape_task(self, id):
        return await self.get_item_with_related(id, 'scrape_task')

    async def get_scrape_parsed_pages_with_scrape_task(self):
        return await self.get_items_with_related('scrape_task')

    async def get_scrape_parsed_page_with_scrape_task_response(self, id):
        return await self.get_item_with_related(id, 'scrape_task_response')

    async def get_scrape_parsed_pages_with_scrape_task_response(self):
        return await self.get_items_with_related('scrape_task_response')

    async def load_scrape_parsed_pages_by_scrape_path_pattern_cache_policy_id(self, scrape_path_pattern_cache_policy_id):
        return await self.load_items(scrape_path_pattern_cache_policy_id=scrape_path_pattern_cache_policy_id)

    async def filter_scrape_parsed_pages_by_scrape_path_pattern_cache_policy_id(self, scrape_path_pattern_cache_policy_id):
        return await self.filter_items(scrape_path_pattern_cache_policy_id=scrape_path_pattern_cache_policy_id)

    async def load_scrape_parsed_pages_by_scrape_task_id(self, scrape_task_id):
        return await self.load_items(scrape_task_id=scrape_task_id)

    async def filter_scrape_parsed_pages_by_scrape_task_id(self, scrape_task_id):
        return await self.filter_items(scrape_task_id=scrape_task_id)

    async def load_scrape_parsed_pages_by_scrape_task_response_id(self, scrape_task_response_id):
        return await self.load_items(scrape_task_response_id=scrape_task_response_id)

    async def filter_scrape_parsed_pages_by_scrape_task_response_id(self, scrape_task_response_id):
        return await self.filter_items(scrape_task_response_id=scrape_task_response_id)

    async def load_scrape_parsed_pages_by_scrape_cycle_run_id(self, scrape_cycle_run_id):
        return await self.load_items(scrape_cycle_run_id=scrape_cycle_run_id)

    async def filter_scrape_parsed_pages_by_scrape_cycle_run_id(self, scrape_cycle_run_id):
        return await self.filter_items(scrape_cycle_run_id=scrape_cycle_run_id)

    async def load_scrape_parsed_pages_by_scrape_cycle_tracker_id(self, scrape_cycle_tracker_id):
        return await self.load_items(scrape_cycle_tracker_id=scrape_cycle_tracker_id)

    async def filter_scrape_parsed_pages_by_scrape_cycle_tracker_id(self, scrape_cycle_tracker_id):
        return await self.filter_items(scrape_cycle_tracker_id=scrape_cycle_tracker_id)

    async def load_scrape_parsed_pages_by_scrape_configuration_id(self, scrape_configuration_id):
        return await self.load_items(scrape_configuration_id=scrape_configuration_id)

    async def filter_scrape_parsed_pages_by_scrape_configuration_id(self, scrape_configuration_id):
        return await self.filter_items(scrape_configuration_id=scrape_configuration_id)

    async def load_scrape_parsed_pages_by_scrape_path_pattern_override_id(self, scrape_path_pattern_override_id):
        return await self.load_items(scrape_path_pattern_override_id=scrape_path_pattern_override_id)

    async def filter_scrape_parsed_pages_by_scrape_path_pattern_override_id(self, scrape_path_pattern_override_id):
        return await self.filter_items(scrape_path_pattern_override_id=scrape_path_pattern_override_id)

    async def load_scrape_parsed_pages_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_parsed_pages_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_parsed_pages_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_parsed_page_ids(self):
        return self.active_item_ids



class ScrapeParsedPageManager(ScrapeParsedPageBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeParsedPageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_parsed_page_manager_instance = ScrapeParsedPageManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import ScrapeQuickFailureLog
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class ScrapeQuickFailureLogDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, scrape_quick_failure_log_item):
        '''Override the base initialization method.'''
        self.id = str(scrape_quick_failure_log_item.id)
        await self._process_core_data(scrape_quick_failure_log_item)
        await self._process_metadata(scrape_quick_failure_log_item)
        await self._initial_validation(scrape_quick_failure_log_item)
        self.initialized = True

    async def _process_core_data(self, scrape_quick_failure_log_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, scrape_quick_failure_log_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, scrape_quick_failure_log_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ScrapeQuickFailureLogDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ScrapeQuickFailureLogBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ScrapeQuickFailureLogDTO
        super().__init__(ScrapeQuickFailureLog, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, scrape_quick_failure_log):
        pass

    async def create_scrape_quick_failure_log(self, **data):
        return await self.create_item(**data)

    async def delete_scrape_quick_failure_log(self, id):
        return await self.delete_item(id)

    async def get_scrape_quick_failure_log_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_scrape_quick_failure_log_by_id(self, id):
        return await self.load_by_id(id)

    async def load_scrape_quick_failure_log(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_scrape_quick_failure_log(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_scrape_quick_failure_logs(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_scrape_quick_failure_logs(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_scrape_quick_failure_log_with_scrape_domain(self, id):
        return await self.get_item_with_related(id, 'scrape_domain')

    async def get_scrape_quick_failure_logs_with_scrape_domain(self):
        return await self.get_items_with_related('scrape_domain')

    async def load_scrape_quick_failure_logs_by_scrape_domain_id(self, scrape_domain_id):
        return await self.load_items(scrape_domain_id=scrape_domain_id)

    async def filter_scrape_quick_failure_logs_by_scrape_domain_id(self, scrape_domain_id):
        return await self.filter_items(scrape_domain_id=scrape_domain_id)

    async def load_scrape_quick_failure_logs_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_scrape_quick_failure_logs_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_scrape_quick_failure_logs_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_scrape_quick_failure_log_ids(self):
        return self.active_item_ids



class ScrapeQuickFailureLogManager(ScrapeQuickFailureLogBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScrapeQuickFailureLogManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

scrape_quick_failure_log_manager_instance = ScrapeQuickFailureLogManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import TaskAssignments
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class TaskAssignmentsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, task_assignments_item):
        '''Override the base initialization method.'''
        self.id = str(task_assignments_item.id)
        await self._process_core_data(task_assignments_item)
        await self._process_metadata(task_assignments_item)
        await self._initial_validation(task_assignments_item)
        self.initialized = True

    async def _process_core_data(self, task_assignments_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, task_assignments_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, task_assignments_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[TaskAssignmentsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TaskAssignmentsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TaskAssignmentsDTO
        super().__init__(TaskAssignments, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_assignments):
        pass

    async def create_task_assignments(self, **data):
        return await self.create_item(**data)

    async def delete_task_assignments(self, id):
        return await self.delete_item(id)

    async def get_task_assignments_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_task_assignments_by_id(self, id):
        return await self.load_by_id(id)

    async def load_task_assignments(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_task_assignments(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_task_assignment(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_task_assignment(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_task_assignments_with_tasks(self, id):
        return await self.get_item_with_related(id, 'tasks')

    async def get_task_assignment_with_tasks(self):
        return await self.get_items_with_related('tasks')

    async def load_task_assignment_by_task_id(self, task_id):
        return await self.load_items(task_id=task_id)

    async def filter_task_assignment_by_task_id(self, task_id):
        return await self.filter_items(task_id=task_id)

    async def load_task_assignment_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_task_assignment_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_task_assignment_by_assigned_by(self, assigned_by):
        return await self.load_items(assigned_by=assigned_by)

    async def filter_task_assignment_by_assigned_by(self, assigned_by):
        return await self.filter_items(assigned_by=assigned_by)

    async def load_task_assignment_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_task_assignments_ids(self):
        return self.active_item_ids



class TaskAssignmentsManager(TaskAssignmentsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TaskAssignmentsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

task_assignments_manager_instance = TaskAssignmentsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import TaskAttachments
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class TaskAttachmentsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, task_attachments_item):
        '''Override the base initialization method.'''
        self.id = str(task_attachments_item.id)
        await self._process_core_data(task_attachments_item)
        await self._process_metadata(task_attachments_item)
        await self._initial_validation(task_attachments_item)
        self.initialized = True

    async def _process_core_data(self, task_attachments_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, task_attachments_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, task_attachments_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[TaskAttachmentsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TaskAttachmentsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TaskAttachmentsDTO
        super().__init__(TaskAttachments, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_attachments):
        pass

    async def create_task_attachments(self, **data):
        return await self.create_item(**data)

    async def delete_task_attachments(self, id):
        return await self.delete_item(id)

    async def get_task_attachments_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_task_attachments_by_id(self, id):
        return await self.load_by_id(id)

    async def load_task_attachments(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_task_attachments(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_task_attachment(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_task_attachment(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_task_attachments_with_tasks(self, id):
        return await self.get_item_with_related(id, 'tasks')

    async def get_task_attachment_with_tasks(self):
        return await self.get_items_with_related('tasks')

    async def load_task_attachment_by_task_id(self, task_id):
        return await self.load_items(task_id=task_id)

    async def filter_task_attachment_by_task_id(self, task_id):
        return await self.filter_items(task_id=task_id)

    async def load_task_attachment_by_uploaded_by(self, uploaded_by):
        return await self.load_items(uploaded_by=uploaded_by)

    async def filter_task_attachment_by_uploaded_by(self, uploaded_by):
        return await self.filter_items(uploaded_by=uploaded_by)

    async def load_task_attachment_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_task_attachments_ids(self):
        return self.active_item_ids



class TaskAttachmentsManager(TaskAttachmentsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TaskAttachmentsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

task_attachments_manager_instance = TaskAttachmentsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import TaskComments
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class TaskCommentsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, task_comments_item):
        '''Override the base initialization method.'''
        self.id = str(task_comments_item.id)
        await self._process_core_data(task_comments_item)
        await self._process_metadata(task_comments_item)
        await self._initial_validation(task_comments_item)
        self.initialized = True

    async def _process_core_data(self, task_comments_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, task_comments_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, task_comments_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[TaskCommentsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TaskCommentsBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TaskCommentsDTO
        super().__init__(TaskComments, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, task_comments):
        pass

    async def create_task_comments(self, **data):
        return await self.create_item(**data)

    async def delete_task_comments(self, id):
        return await self.delete_item(id)

    async def get_task_comments_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_task_comments_by_id(self, id):
        return await self.load_by_id(id)

    async def load_task_comments(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_task_comments(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_task_comment(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_task_comment(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_task_comments_with_tasks(self, id):
        return await self.get_item_with_related(id, 'tasks')

    async def get_task_comment_with_tasks(self):
        return await self.get_items_with_related('tasks')

    async def load_task_comment_by_task_id(self, task_id):
        return await self.load_items(task_id=task_id)

    async def filter_task_comment_by_task_id(self, task_id):
        return await self.filter_items(task_id=task_id)

    async def load_task_comment_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_task_comment_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_task_comment_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_task_comments_ids(self):
        return self.active_item_ids



class TaskCommentsManager(TaskCommentsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TaskCommentsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

task_comments_manager_instance = TaskCommentsManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import UserPreferences
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class UserPreferencesDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, user_preferences_item):
        '''Override the base initialization method.'''
        self.id = str(user_preferences_item.id)
        await self._process_core_data(user_preferences_item)
        await self._process_metadata(user_preferences_item)
        await self._initial_validation(user_preferences_item)
        self.initialized = True

    async def _process_core_data(self, user_preferences_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, user_preferences_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, user_preferences_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[UserPreferencesDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class UserPreferencesBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or UserPreferencesDTO
        super().__init__(UserPreferences, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, user_preferences):
        pass

    async def create_user_preferences(self, **data):
        return await self.create_item(**data)

    async def delete_user_preferences(self, id):
        return await self.delete_item(id)

    async def get_user_preferences_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_user_preferences_by_id(self, id):
        return await self.load_by_id(id)

    async def load_user_preferences(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_user_preferences(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_user_preference(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_user_preference(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def load_user_preference_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_user_preference_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_user_preference_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_user_preferences_ids(self):
        return self.active_item_ids



class UserPreferencesManager(UserPreferencesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserPreferencesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

user_preferences_manager_instance = UserPreferencesManager()


from dataclasses import dataclass
from database.orm.core.extended import BaseManager, BaseDTO
from database.orm.models import WcInjury
from typing import Optional, Type, Any
from common import vcprint

@dataclass
class WcInjuryDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, wc_injury_item):
        '''Override the base initialization method.'''
        self.id = str(wc_injury_item.id)
        await self._process_core_data(wc_injury_item)
        await self._process_metadata(wc_injury_item)
        await self._initial_validation(wc_injury_item)
        self.initialized = True

    async def _process_core_data(self, wc_injury_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, wc_injury_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, wc_injury_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[WcInjuryDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class WcInjuryBase(BaseManager):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or WcInjuryDTO
        super().__init__(WcInjury, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, wc_injury):
        pass

    async def create_wc_injury(self, **data):
        return await self.create_item(**data)

    async def delete_wc_injury(self, id):
        return await self.delete_item(id)

    async def get_wc_injury_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_wc_injury_by_id(self, id):
        return await self.load_by_id(id)

    async def load_wc_injury(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_wc_injury(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_wc_injuries(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_wc_injuries(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_wc_injury_with_wc_impairment_definition(self, id):
        return await self.get_item_with_related(id, 'wc_impairment_definition')

    async def get_wc_injuries_with_wc_impairment_definition(self):
        return await self.get_items_with_related('wc_impairment_definition')

    async def get_wc_injury_with_wc_report(self, id):
        return await self.get_item_with_related(id, 'wc_report')

    async def get_wc_injuries_with_wc_report(self):
        return await self.get_items_with_related('wc_report')

    async def load_wc_injuries_by_report_id(self, report_id):
        return await self.load_items(report_id=report_id)

    async def filter_wc_injuries_by_report_id(self, report_id):
        return await self.filter_items(report_id=report_id)

    async def load_wc_injuries_by_impairment_definition_id(self, impairment_definition_id):
        return await self.load_items(impairment_definition_id=impairment_definition_id)

    async def filter_wc_injuries_by_impairment_definition_id(self, impairment_definition_id):
        return await self.filter_items(impairment_definition_id=impairment_definition_id)

    async def load_wc_injuries_by_side(self, side):
        return await self.load_items(side=side)

    async def filter_wc_injuries_by_side(self, side):
        return await self.filter_items(side=side)

    async def load_wc_injuries_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_wc_injury_ids(self):
        return self.active_item_ids



class WcInjuryManager(WcInjuryBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WcInjuryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

wc_injury_manager_instance = WcInjuryManager()