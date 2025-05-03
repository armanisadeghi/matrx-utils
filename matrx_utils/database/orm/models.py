from ...core.initialize_database import model_module

def __getattr__(name):
    if model_module is None:
        raise ImportError("Models not initialized. Please call matrx_utils.init() first.")
    return getattr(model_module, name)