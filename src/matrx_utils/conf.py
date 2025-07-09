import os
from matrx_utils import vcprint, redact_object


info = True
debug = False

_restricted_env_vars = {'PATH', 'HOME', 'USER', 'PYTHONPATH'} # Case Sensitive
_restricted_service_names = {'admin', 'admin_service', 'log', 'log_service'} # Case Insensitive
_restricted_task_and_definitions = {'mic_check', 'mic_check_definition','process_task', 'execute_task', '__init__', 'update_attributes', 'add_stream_handler'} # Case Insensitive
_restricted_fields_names = {'stream_handler'}

class NotConfiguredError(Exception):
    pass


class LazySettings:
    _settings_object = None
    _configured = False
    _env_first = False
    _reported_settings = set()
    _env_cache = {}
    _env_cache_loaded = False
    _restricted_env_vars = _restricted_env_vars
    _verbose_mode = False

    def __init__(self, env_first=False):
        self._env_first = env_first
        self._reported_settings = set()
        self._env_cache = {}
        self._env_cache_loaded = False
        self._verbose_mode = False

    def _ensure_configured(self):
        if not self._configured:
            raise NotConfiguredError("Call matrx_utils.conf.configure() first.")

    def _load_env_cache(self):
        """Load all environment variables into cache once"""
        if not self._env_cache_loaded:
            self._env_cache = dict(os.environ)
            self._env_cache_loaded = True

    def _get_env_with_fallback(self, name):
        """Get environment variable with fallback to live lookup and caching"""
        name_upper = name.upper()

        # First check cache
        if name_upper in self._env_cache:
            return self._env_cache[name_upper]

        # Fallback to live environment lookup
        live_value = os.getenv(name_upper)
        if live_value is not None:
            # Cache the newly found value
            self._env_cache[name_upper] = live_value
            return live_value

        return None

    def _convert_to_bool(self, value):
        """Convert string values 'true' or 'false' (case-insensitive) to boolean."""
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
        return value

    def __getattr__(self, name):
        self._load_env_cache()  # Ensure env cache is loaded

        if self._env_first:
            # Check environment first
            env_value = self._get_env_with_fallback(name)
            if env_value is not None:
                converted_value = self._convert_to_bool(env_value)
                return converted_value

            # Then check configured settings
            if self._configured:
                try:
                    value = getattr(self._settings_object, name)
                    return value
                except AttributeError:
                    pass

            # Final fallback - check environment one more time for edge cases
            final_env_check = self._get_env_with_fallback(name)
            if final_env_check is not None:
                converted_value = self._convert_to_bool(final_env_check)
                return converted_value

            # Not found anywhere
            if name not in self._reported_settings:
                self._reported_settings.add(name)
            if not self._configured:
                raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")
            else:
                raise AttributeError(f"Setting '{name}' not found in environment or configured settings")
        else:
            # Check configured settings first
            if self._configured:
                try:
                    value = getattr(self._settings_object, name)
                    return value
                except AttributeError:
                    # Settings object doesn't have it, check environment
                    env_value = self._get_env_with_fallback(name)
                    if env_value is not None:
                        converted_value = self._convert_to_bool(env_value)
                        return converted_value

                    # Not found anywhere
                    if name not in self._reported_settings:
                        self._reported_settings.add(name)
                    raise AttributeError(f"Setting '{name}' not found in configured settings or environment")

            # Not configured, check environment
            env_value = self._get_env_with_fallback(name)
            if env_value is not None:
                converted_value = self._convert_to_bool(env_value)
                return converted_value

            # Not found anywhere
            if name not in self._reported_settings:
                self._reported_settings.add(name)
            raise NotConfiguredError(f"Settings not configured and '{name}' not found in environment variables")

    def reset_env_variables(self):
        """Reload all environment variables from system"""
        self._env_cache = dict(os.environ)
        self._env_cache_loaded = True
        if self._verbose_mode:
            vcprint(f"Reloaded {len(self._env_cache)} environment variables", verbose=True, color="blue")

    def list_settings(self):
        """List all settings as flat key-value pairs (unredacted)"""
        self._load_env_cache()
        all_settings = {}

        # Add environment variables from cache
        for key, value in self._env_cache.items():
            all_settings[key] = self._convert_to_bool(value)

        # Add settings object attributes
        if self._configured and self._settings_object:
            for attr_name in dir(self._settings_object):
                if not attr_name.startswith('_'):
                    try:
                        value = getattr(self._settings_object, attr_name)
                        if not callable(value):
                            all_settings[attr_name.upper()] = value
                    except AttributeError:
                        pass

        return all_settings

    def list_settings_redacted(self):
        """List all settings as flat key-value pairs (with smart redaction)"""
        all_settings = self.list_settings()
        return redact_object(all_settings)
    

    def set_env_setting(self, name, value):
        """Set an environment variable setting (only for env vars, not settings object attrs)"""
        name_upper = name.upper()

        if name_upper in self._restricted_env_vars:
            raise ValueError(f"Cannot modify restricted environment variable: {name_upper}")

        # Convert value to string for environment variables
        str_value = str(value)

        # Update both cache and actual environment
        self._env_cache[name_upper] = str_value
        os.environ[name_upper] = str_value

        if self._verbose_mode:
            vcprint(f"Set environment variable {name_upper} = {str_value}", verbose=True, color="green")

    def get_env_setting(self, name):
        """Get an environment variable setting"""
        return self._get_env_with_fallback(name)

    def list_env_settings(self):
        """List all cached environment variables"""
        # Return live environment variables to ensure accuracy
        return dict(os.environ)



settings = LazySettings()


def configure_settings(settings_object, env_first=False, verbose=False):
    """Configure settings with optional verbose mode"""
    if settings._configured:
        raise RuntimeError("Settings have already been configured and cannot be reconfigured.")

    if settings_object is None:
        raise ValueError("Settings object cannot be None.")

    settings._settings_object = settings_object
    settings._configured = True
    settings._env_first = env_first
    settings._verbose_mode = verbose
    settings._reported_settings.clear()  # Clear reported settings on configuration

    if verbose:
        vcprint(f"Configured settings with env_first: {env_first}, verbose: {verbose}", verbose=True, color="blue")