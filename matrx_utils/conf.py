import os
from matrx_utils.fancy_prints import vcprint, redact_object


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


def configure_context(getter) -> None:
    """Register a callable that returns the active request-scoped user context.

    Call this once at app startup, after your middleware is configured.
    The getter is called on every resolution attempt and must return an object
    with at least a ``.user_id: str`` attribute, or ``None``.

    Once registered, matrx-utils features (cloud_sync managed operations, etc.)
    automatically resolve the current user without requiring explicit ``user_id``
    arguments in every call.

    Parameters
    ----------
    getter:
        A zero-argument callable that returns a context object (or None).
        Must be safe to call from any async coroutine or thread.

    Examples
    --------
    aidream / matrx-connect — pass ``try_get_app_context`` directly::

        from matrx_utils.conf import configure_context
        from matrx_connect.context.app_context import try_get_app_context
        configure_context(try_get_app_context)

    Any other FastAPI / Django app with a request-local::

        from matrx_utils.conf import configure_context
        configure_context(lambda: getattr(request_local, "ctx", None))

    Background scripts / tests — use ``set_manual_context`` instead::

        from matrx_utils.ctx import set_manual_context, SimpleUserContext
        token = set_manual_context(SimpleUserContext(user_id="test-uuid"))
        # ... do work ...
        from matrx_utils.ctx import clear_manual_context
        clear_manual_context(token)
    """
    from matrx_utils import ctx as _ctx
    _ctx._context_getter = getter


# ---------------------------------------------------------------------------
# Host-specific callbacks for the cloud-sync file pipeline.
#
# Each callback is OPTIONAL — matrx-utils ships with safe no-op defaults so
# a standalone install runs end-to-end without any injection. Hosts that need
# the corresponding behaviour register a callable here at startup.
#
# Callbacks live in module-global slots (rather than ContextVars) because
# they're cross-cutting infrastructure injections, not per-request state.
# ---------------------------------------------------------------------------

# The active CDN-purge callback. Signature: ``(urls: list[str]) -> None``.
# Fire-and-forget — matrx-utils never awaits or checks the return value.
# Invoked from ``SyncEngine.change_visibility_async`` and the hard-delete
# / variant-replace paths whenever a CDN URL needs to be invalidated.
_cdn_purger = None


def configure_cdn_purger(purger) -> None:
    """Register the host's CDN purge callback.

    matrx-utils invokes the registered callable whenever a public file's
    URL needs to be invalidated (visibility changes, hard delete, variant
    replacement). The callback receives a ``list[str]`` of CDN URLs and
    should fire-and-forget — matrx-utils does not wait on the result.

    Hosts using Cloudflare typically wire ``schedule_purge``; hosts on
    other CDNs wire their equivalent. If unset, CDN purges silently no-op
    and the ``?v=<checksum>`` URL cache-buster handles content updates.
    """
    global _cdn_purger
    _cdn_purger = purger


def get_cdn_purger():
    """Return the registered CDN purger, or ``None`` if unset."""
    return _cdn_purger


# The active quota pre-flight check. Signature:
#   async (user_id, size, *, is_guest, bypass) -> QuotaDecisionLike
# Returns an object with .allowed / .reason / .details — matrx-utils raises
# QuotaExceededError when decision.allowed is False. Hosts wire their
# billing/tier system here; standalone installs accept every upload.
_quota_check = None


def configure_quota_check(check) -> None:
    """Register the host's pre-upload quota check.

    The callable is awaited at upload time with the requested size in bytes.
    A return-value duck-typed as ``{allowed: bool, reason: str | None, ...}``
    is accepted. When ``allowed`` is False the upload pipeline raises
    ``matrx_utils.file_handling.errors.QuotaExceededError(decision)``.
    """
    global _quota_check
    _quota_check = check


def get_quota_check():
    return _quota_check


# The active audit-event logger. Signature: ``(event_type: str, payload: dict) -> None``.
# Invoked by matrx-utils on every file mutation that hosts may want to track
# (visibility change, hard delete, share-link create/revoke, guest migration).
# Standalone installs leave this unset and the calls become no-ops.
_audit_logger = None


def configure_audit_logger(logger) -> None:
    """Register the host's audit-event logger.

    matrx-utils calls ``logger(event_type, payload)`` on every file
    mutation worth tracking. Hosts typically bridge this to Sentry
    breadcrumbs + a cld_events outbox write.
    """
    global _audit_logger
    _audit_logger = logger


def get_audit_logger():
    return _audit_logger