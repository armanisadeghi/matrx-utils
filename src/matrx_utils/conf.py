import os
from matrx_utils import vcprint

info = True
debug = False


class NotConfiguredError(Exception):
    pass


class LazySettings:
    _settings_object = None
    _configured = False
    _env_first = False  # Default: settings first
    _reported_settings = set()  # Track reported missing settings

    def __init__(self, env_first=False):
        self._env_first = env_first
        self._reported_settings = set()  # Initialize the set
        vcprint(f"Initialized LazySettings with env_first: {self._env_first}", verbose=info,
                color="blue")  # Critical: initialization

    def _ensure_configured(self):
        if not self._configured:
            vcprint("Settings not configured, raising NotConfiguredError", verbose=info, color="red")  # Critical: error
            raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def _convert_to_bool(self, value):
        """Convert string values 'true' or 'false' (case-insensitive) to boolean."""
        if isinstance(value, str):
            if value.lower() == 'true':
                vcprint(f"Converted '{value}' to True", verbose=debug, color="green")  # Non-critical: conversion
                return True
            if value.lower() == 'false':
                vcprint(f"Converted '{value}' to False", verbose=debug, color="green")  # Non-critical: conversion
        return value

    def __getattr__(self, name):
        vcprint(f"Looking up setting '{name}'", verbose=debug, color="cyan")  # Non-critical: lookup start

        if self._env_first:
            vcprint("Checking environment variables first due to env_first=True", verbose=debug,
                    color="yellow")  # Non-critical: precedence
            env_value = os.getenv(name.upper())
            if env_value is not None:
                vcprint(f"Found '{name.upper()}' in environment variables", verbose=info,
                        color="green")  # Critical: found value
                return self._convert_to_bool(env_value)
            if self._configured:
                try:
                    vcprint(f"Checking configured settings for '{name}'", verbose=debug,
                            color="yellow")  # Non-critical: checking settings
                    return getattr(self._settings_object, name)
                except AttributeError:
                    if name not in self._reported_settings:
                        vcprint(f"Setting '{name}' not found in configured settings", verbose=info,
                                color="red")  # Critical: error
                        self._reported_settings.add(name)  # Mark as reported
                    raise AttributeError(f"Setting '{name}' not found in environment or configured settings")
            if name not in self._reported_settings:
                vcprint(f"Settings not configured and '{name}' not found in environment variables", verbose=info,
                        color="red")  # Critical: error
                self._reported_settings.add(name)  # Mark as reported
            raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")

        else:
            vcprint("Checking configured settings first due to env_first=False", verbose=debug,
                    color="yellow")  # Non-critical: precedence
            if self._configured:
                try:
                    vcprint(f"Found '{name}' in configured settings", verbose=info,
                            color="green")  # Critical: found value
                    return getattr(self._settings_object, name)
                except AttributeError:
                    vcprint(f"Setting '{name}' not found in configured settings, checking environment", verbose=debug,
                            color="yellow")  # Non-critical: fallback
                    env_value = os.getenv(name.upper())
                    if env_value is not None:
                        vcprint(f"Found '{name.upper()}' in environment variables", verbose=info,
                                color="green")  # Critical: found value
                        return self._convert_to_bool(env_value)
                    if name not in self._reported_settings:
                        vcprint(f"Setting '{name}' not found in configured settings or environment", verbose=info,
                                color="red")  # Critical: error
                        self._reported_settings.add(name)  # Mark as reported
                    raise AttributeError(f"Setting '{name}' not found in configured settings or environment")
            env_value = os.getenv(name.upper())
            if env_value is not None:
                vcprint(f"Found '{name}' in environment variables", verbose=info,
                        color="green")  # Critical: found value
                return self._convert_to_bool(env_value)
            if name not in self._reported_settings:
                vcprint(f"Settings not configured and '{name}' not found in environment variables", verbose=info,
                        color="red")  # Critical: error
                self._reported_settings.add(name)  # Mark as reported
            raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")


settings = LazySettings()


def configure_settings(settings_object, env_first=False):
    if settings_object is None:
        vcprint("Settings object is None, raising ValueError", verbose=info, color="red")  # Critical: error
        raise ValueError("Settings object cannot be None.")
    settings._settings_object = settings_object
    settings._configured = True
    settings._env_first = env_first
    settings._reported_settings.clear()  # Clear reported settings on configuration
    vcprint(f"Configured settings with env_first: {env_first}", verbose=info, color="blue")  # Critical: configuration