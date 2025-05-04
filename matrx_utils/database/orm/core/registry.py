# matrx_utils\database\orm\core\registry.py

from matrx_utils import vcprint


class ModelRegistry:
    _models = {}
    _initialized = False

    @classmethod
    def register(cls, model_class):
        model_name = model_class.__name__
        if model_name in cls._models and cls._models[model_name] is not model_class:
            raise ValueError(f"Model {model_name} is already registered")
        cls._models[model_name] = model_class

    @classmethod
    def register_all(cls, models):
        for model in models:
            cls.register(model)

    @classmethod
    def get_model(cls, model_name):
        model = cls._models.get(model_name)
        return model

    @classmethod
    def all_models(cls):
        return cls._models.copy()

    @classmethod
    def clear(cls):
        cls._models.clear()
        cls._initialized = False
        vcprint("Cleared all registered models", color="yellow", inline=True)


model_registry = ModelRegistry()


def get_model_by_name(model_name):
    model = model_registry.get_model(model_name)
    if model is None:
        raise ValueError(f"Model {model_name} not found: {model_name}")
    return model
