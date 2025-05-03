import os
import importlib.util
from matrx_utils.schema_builder.generate_schema import generate_all
from matrx_utils.conf import settings


model_module = None

def init():
    generate_all()
    global model_module
    model_file_path = os.path.join(settings.ADMIN_SAVE_DIRECT_ROOT,"database/orm/models.py")
    spec = importlib.util.spec_from_file_location("dynamic_models", model_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model_module = module
