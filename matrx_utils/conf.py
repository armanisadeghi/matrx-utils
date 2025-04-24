# matrx_utils/conf.py
class NotConfiguredError(Exception): pass

class LazySettings:
    _settings_object = None
    _configured = False

    def _ensure_configured(self):
        if not self._configured: raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def __getattr__(self, name):
        self._ensure_configured()
        try:
            return getattr(self._settings_object, name)
        except AttributeError:
            raise AttributeError(f"Setting '{name}' not found.")

settings = LazySettings()

def configure(settings_object):
    if settings_object is None: raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True