# matrx_utils\socket\core\app_factory.py
AppServiceFactory = None

class AlreadyConfiguredFactoryError(Exception):
    pass

class FactoryNotConfiguredError(Exception):
    pass

def configure_factory(class_object):
    global AppServiceFactory
    if AppServiceFactory is not None:
        raise AlreadyConfiguredFactoryError("Factory is already configured.")

    AppServiceFactory = class_object

def get_app_factory():
    global AppServiceFactory
    if not AppServiceFactory:
        raise FactoryNotConfiguredError("Please configure App service factory")

    return AppServiceFactory()

