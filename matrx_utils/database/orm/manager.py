# matrx_utils\database\orm\manager.py
from ...core.initialize_database import manager_module


def __getattr__(name):
    if manager_module is None:
        raise ImportError("Managers not initialized. Please call matrx_utils.init() first.")
    return getattr(manager_module, name)
