# matrx_utils/conf.py

from matrx_utils import vcprint
from pathlib import Path

class NotConfiguredError(Exception): pass

class LazySettingsDev:
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

settings = LazySettingsDev()
vcprint("WARNING USING DEV SETTINGS AT PACKAGE LEVEL", color="yellow")

def configure(settings_object):
    if settings_object is None: raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True


class DefaultSettings:
    BASE_DIR: Path = Path.cwd()
    TEMP_DIR: Path = Path.cwd() / "temp" # Default temp in CWD
    LOG_VCPRINT: bool = True
    DEBUG: bool = True


configure(DefaultSettings())