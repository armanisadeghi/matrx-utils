import os
from matrx_utils import vcprint

class NotConfiguredError(Exception):
    pass

class LazySettings:
    _settings_object = None
    _configured = False
    _env_first = False  # Default: settings first

    def __init__(self, env_first=False):
        self._env_first = env_first
        vcprint(f"Initialized LazySettings with env_first: {self._env_first}", color="blue")

    def _ensure_configured(self):
        if not self._configured:
            raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def __getattr__(self, name):
        vcprint(f"Looking up setting '{name}'", color="cyan")
        
        if self._env_first:
            vcprint("Checking environment variables first due to env_first=True", color="yellow")
            env_value = os.getenv(name.upper())
            if env_value is not None:
                vcprint(f"Found '{name.upper()}' in environment variables", color="green")
                return env_value
            if self._configured:
                try:
                    vcprint(f"Checking configured settings for '{name}'", color="yellow")
                    return getattr(self._settings_object, name)
                except AttributeError:
                    vcprint(f"Setting '{name}' not found in configured settings", color="red")
                    raise AttributeError(f"Setting '{name}' not found in environment or configured settings")
            raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")
        
        else:
            vcprint("Checking configured settings first due to env_first=False", color="yellow")
            if self._configured:
                try:
                    vcprint(f"Found '{name}' in configured settings", color="green")
                    return getattr(self._settings_object, name)
                except AttributeError:
                    vcprint(f"Setting '{name}' not found in configured settings, checking environment", color="yellow")
                    env_value = os.getenv(name.upper())
                    if env_value is not None:
                        vcprint(f"Found '{name.upper()}' in environment variables", color="green")
                        return env_value
                    raise AttributeError(f"Setting '{name}' not found in configured settings or environment")
            env_value = os.getenv(name.upper())
            if env_value is not None:
                vcprint(f"Found '{name}' in environment variables", color="green")
                return env_value
            raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")

settings = LazySettings()

def configure_settings(settings_object, env_first=False):
    if settings_object is None:
        raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True
    settings._env_first = env_first
    vcprint(f"Configured settings with env_first: {env_first}", color="blue")