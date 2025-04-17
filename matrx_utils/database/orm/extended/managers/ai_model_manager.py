from database.orm.extended.managers.ai_model_base import AiModelBase
from matrix.ai_models.ai_model_manager import update_data_in_code
import os
import asyncio
from common import vcprint


class AiModelManager(AiModelBase):
    def __init__(self):
        super().__init__()

    async def get_model(self, model_id: str):
        model = await self.load_by_id(model_id)
        return model

    async def get_models(self):
        models = await self.load_ai_models()
        return models

    async def load_model_by_name(self, model_name: str):
        model = await self.load_ai_models(name=model_name)
        return model

    async def load_model_by_provider(self, provider: str):
        model = await self.load_ai_models(provider=provider)
        return model

    async def list_unique_model_providers(self, update_data_in_code: bool = False):
        models = await self.load_ai_models()
        providers = list(set([model.provider for model in models]))
        if update_data_in_code:
            await self.update_data_in_code(providers, "model_providers")
        return providers

    async def update_models_in_code(self):
        models = await self.load_ai_models()
        await self.update_data_in_code(models, "all_active_ai_models")

    async def update_data_in_code(self, data, variable_name):
        update_data_in_code(variable_name, data)


async def local_test(test_type: str, **kwargs):
    manager = AiModelManager()

    update_data = kwargs.get("update_data_in_code", False)

    if test_type == "id":
        data = await manager.get_model("dd45b76e-f470-4765-b6c4-1a275d7860bf")
    elif test_type == "name":
        data = await manager.filter_ai_models_by_name("gpt-4o")
    elif test_type == "provider":
        data = await manager.load_ai_models_by_provider("OpenAI")
    elif test_type == "all_models":
        data = await manager.load_ai_models(update_data_in_code=update_data)
    elif test_type == "list_providers":
        data = await manager.list_unique_model_providers(update_data_in_code=update_data)
    else:
        raise ValueError(f"Invalid test type: {test_type}")

    return data


if __name__ == "__main__":
    os.system("cls")

    test_type = "name"  # ["id", "name", "provider", "all_models", "list_providers"]

    data = asyncio.run(local_test(test_type, update_data_in_code=True))

    vcprint(data=data, title="AI Model", pretty=True, color="green")
