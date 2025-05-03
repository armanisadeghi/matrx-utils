AppServiceFactory = None

class AlreadyConfiguredFactoryError(Exception):
    pass

def configure_factory(class_object):
    global AppServiceFactory
    if AppServiceFactory is not None:
        raise AlreadyConfiguredFactoryError("Factory is already configured.")

    AppServiceFactory = class_object

