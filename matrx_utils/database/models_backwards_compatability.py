from database.orm.models import CompiledRecipe, DataBroker, Recipe
from recipes.compiled.new_utils import update_content_with_runtime_brokers
from common import vcprint
from dataclasses import dataclass
from database.orm.core.extended import BaseDTO, BaseManager

verbose = False
debug = False
info = True


# Example with some useful recipe-related methods
class RecipeManagerTwo(BaseManager):
    def __init__(self):
        super().__init__(Recipe)

    def _initialize_manager(self):
        super()._initialize_manager()
        self.computed_fields.add("version_count")
        self.computed_fields.add("has_compiled_versions")
        self.relation_fields.add("compiled_recipes")

    async def _initialize_runtime_data(self, recipe):
        recipe.runtime.version_count = None
        recipe.runtime.latest_version = None
        recipe.runtime.has_compiled_versions = False

    async def get_latest_compiled_version(self, recipe):
        if not recipe.runtime.latest_version:
            versions = await recipe.fetch_ifk("compiled_recipes")
            recipe.runtime.latest_version = max(v.version for v in versions) if versions else 0
        return recipe.runtime.latest_version


class CompiledRecipeManagerTwo(BaseManager):
    def __init__(self):
        super().__init__(CompiledRecipe)

    def _initialize_manager(self):
        super()._initialize_manager()
        self.computed_fields.add("is_latest")
        self.relation_fields.add("recipe")

    async def _initialize_runtime_data(self, recipe):
        recipe.runtime.is_latest = None
        recipe.runtime.parent_recipe = None

    async def check_if_latest(self, compiled_recipe):
        if compiled_recipe.runtime.is_latest is None:
            recipe = await compiled_recipe.fetch_fk("recipe_id")
            if recipe:
                latest = await recipe.fetch_ifk("compiled_recipes")
                compiled_recipe.runtime.is_latest = (compiled_recipe.version == max(v.version for v in latest)) if latest else True
        return compiled_recipe.runtime.is_latest


@dataclass
class DataBrokerDTO(BaseDTO):
    id: str
    name: str
    data_type: str = "str"
    default_value: str = None
    input_component_id: str = None
    output_component_id: str = None
    color: str = "blue"
    message_brokers: list = None
    message_count: int = None
    is_active: bool = False
    last_used: str = None

    @classmethod
    async def from_model(cls, model):
        return cls(
            id=str(model.id),
            name=model.name,
            data_type=model.data_type,
            default_value=model.default_value,
            input_component_id=str(model.input_component) if model.input_component else None,
            output_component_id=str(model.output_component) if model.output_component else None,
            color=model.color,
        )


class DataBrokerManager(BaseManager):
    def __init__(self):
        super().__init__(DataBroker, DataBrokerDTO)

    async def _initialize_dto_runtime(self, dto, item):
        dto.message_brokers = await item.fetch_ifk("message_brokers")
        dto.message_count = len(dto.message_brokers) if dto.message_brokers else 0


@dataclass
class CompiledRecipeDTO(BaseDTO):
    id: str
    recipe_id: str
    version: int
    brokers: list = None
    raw_messages: list = None
    clean_messages: list = None
    ready_messages: list = None
    settings: list = None

    @classmethod
    async def from_model(cls, model):
        import json

        compiled_data = json.loads(model.compiled_recipe) if isinstance(model.compiled_recipe, str) else model.compiled_recipe

        brokers = [
            {
                "id": broker["id"],
                "default_value": broker.get("defaultValue"),
                "value": broker.get("defaultValue"),
                "ready": False,
            }
            for broker in compiled_data.get("brokers", [])
        ]

        raw_messages = compiled_data.get("messages", [])
        clean_messages = update_content_with_runtime_brokers(raw_messages, brokers)
        ready_messages = update_content_with_runtime_brokers(clean_messages, brokers)

        return cls(
            id=str(model.id),
            recipe_id=str(model.recipe_id),
            version=model.version,
            brokers=brokers,
            raw_messages=raw_messages,
            clean_messages=clean_messages,
            ready_messages=ready_messages,
            settings=compiled_data.get("settings", []),
        )

    def update_broker_value(self, broker_id: str, value: str):
        vcprint(
            {"broker_id": broker_id, "value": value},
            "[COMPILED RECIPE DTO] Updating Broker Value",
            verbose=True,
            pretty=True,
            color="yellow",
        )
        for broker in self.brokers:
            if broker["id"] == broker_id:
                broker["value"] = value
                broker["ready"] = True
                break
        vcprint(
            self.brokers,
            "[COMPILED RECIPE DTO] All Brokers",
            verbose=True,
            pretty=True,
            color="yellow",
        )
        self._update_messages()

    def update_broker_values(self, broker_values: dict):
        for broker in broker_values:
            self.update_broker_value(broker["id"], broker["value"])

    def add_broker(self, broker):
        vcprint(broker, "Broker", verbose=debug, pretty=True, color="yellow")
        broker_id = broker.id if hasattr(broker, "id") else broker["id"]
        default_value = broker.default_value if hasattr(broker, "default_value") else broker.get("defaultValue")

        # Check if broker already exists
        existing_broker = next((broker for broker in self.brokers if broker["id"] == broker_id), None)

        if existing_broker:
            # Update existing broker's value and ready status
            existing_broker["value"] = default_value
            existing_broker["ready"] = True
        else:
            # Add new broker
            new_broker = {
                "id": broker_id,
                "default_value": default_value,
                "value": default_value,
                "ready": False,
            }
            self.brokers.append(new_broker)

        self._update_messages()

    def _update_messages(self):
        self.clean_messages = update_content_with_runtime_brokers(self.raw_messages, self.brokers)
        self.ready_messages = update_content_with_runtime_brokers(self.clean_messages, self.brokers)

    def get_final_structure(self):
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "version": self.version,
            "messages": self.ready_messages,
            "settings": self.settings,
        }

    def to_dict(self) -> dict:
        return {key: getattr(self, key) for key in self.__annotations__ if getattr(self, key) is not None}


class CompiledRecipeManager(BaseManager):
    def __init__(self):
        super().__init__(CompiledRecipe, CompiledRecipeDTO)

    async def get_final_structure(self, compiled_recipe_id: str):
        item = await self.load_item(id=compiled_recipe_id)
        return item.runtime.dto.get_final_structure() if item else None

    async def update_broker_value(self, compiled_recipe_id: str, broker_id: str, value: str):
        item = await self.load_item(id=compiled_recipe_id)
        if item and item.runtime.dto:
            item.runtime.dto.update_broker_value(broker_id, value)
            return item.runtime.dto.to_dict()
        return None

    async def update_broker_values(self, compiled_recipe_id: str, broker_values: dict):
        item = await self.load_item(id=compiled_recipe_id)
        if item and item.runtime.dto:
            item.runtime.dto.update_broker_values(broker_values)
            return item.runtime.dto.to_dict()
        return None

    async def add_broker(self, compiled_recipe_id: str, broker):
        item = await self.load_item(id=compiled_recipe_id)
        if item and item.runtime.dto:
            item.runtime.dto.add_broker(broker)
            return item.runtime.dto.to_dict()
        return None

    async def get_brokers(self, compiled_recipe_id: str):
        item = await self.load_item(id=compiled_recipe_id)
        return item.runtime.dto.brokers if item else None

    # If we need to find all compiled versions for a recipe:
    async def get_compiled_versions_for_recipe(self, recipe_id: str):
        return await self.model.filter(recipe_id=recipe_id).all()
