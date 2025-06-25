import os

from matrx_utils import vcprint


class NotConfiguredError(Exception):
    pass


class LazySettings:
    _settings_object = None
    _configured = False

    def _ensure_configured(self):
        if not self._configured:
            raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def __getattr__(self, name):
        if self._configured:
            try:
                return getattr(self._settings_object, name)
            except AttributeError:
                vcprint(f"Setting '{name}' not found in configured settings, checking environment", verbose=True,
                        color="yellow")
                env_value = os.getenv(name.upper())
                if env_value is not None:
                    vcprint(f"Found '{name.upper()}' in environment", color="yellow")
                    return env_value
                else:
                    raise AttributeError(f"Setting '{name}' not found in configured settings or environment variables.")
        else:
            # Settings not configured, check environment directly
            vcprint("Settings have not been configured, checking environment variables...", color="yellow")
            env_value = os.getenv(name.upper())
            if env_value is not None:
                vcprint(f"Found '{name}' in environment variables", color="yellow")
                return env_value
            else:
                raise NotConfiguredError(
                    f"Settings not configured and '{name}' not found in environment variables. Either configure settings with matrx_utils.conf.configure() or set {name.upper()} environment variable.")


settings = LazySettings()


def configure_settings(settings_object):
    if settings_object is None:
        raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True
