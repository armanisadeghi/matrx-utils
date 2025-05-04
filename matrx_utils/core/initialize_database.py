# matrx_utils\core\initialize_database.py
import os
import importlib.util
from matrx_utils.schema_builder.generate_schema import generate_all
from matrx_utils.conf import settings

model_module = None
manager_module = None


def init():
    generate_all()
    global model_module, manager_module

    # Import model_module
    model_file_path = os.path.join(settings.ADMIN_PYTHON_ROOT_DIR, "database/orm/models.py")
    spec = importlib.util.spec_from_file_location("matrx_utils.database.models", model_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model_module = module

    # Import manager_module
    manager_file_path = os.path.join(settings.ADMIN_PYTHON_ROOT_DIR, "database/orm/extended/managers/all_managers.py")
    spec = importlib.util.spec_from_file_location("matrx_utils.database.managers", manager_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manager_module = module