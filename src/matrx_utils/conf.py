from pathlib import Path

from matrx_utils import vcprint

DEV_MODE = False


class NotConfiguredError(Exception): 
    pass


class LazySettings:
    _settings_object = None
    _configured = False

    def _ensure_configured(self):
        if not self._configured: 
            raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def __getattr__(self, name):
        self._ensure_configured()
        try:
            return getattr(self._settings_object, name)
        except AttributeError:
            raise AttributeError(f"Setting '{name}' not found.")


settings = LazySettings()


def configure_settings(settings_object):
    if settings_object is None: 
        raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True


if DEV_MODE:
    vcprint("DEV_MODE is being used in matrx_utils.conf", color="light_yellow")


    class DevSettings:
        BASE_DIR: Path = Path(r"D:\work\matrx-utils")
        TEMP_DIR: Path = BASE_DIR / "temp"
        LOG_VCPRINT: bool = True
        DEBUG: bool = True
        SAVE_DIRECT_SCHEMA = True


    configure_settings(DevSettings())
