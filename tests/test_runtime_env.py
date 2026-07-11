"""Tests for the two-axis host identity resolver (matrx_utils.runtime_env).

These exercise the resolver directly via monkeypatched env + reset cache, so
they do not depend on the ambient process env. Note pytest itself sets
PYTEST_CURRENT_TEST, so we clear it in cases that must reach the MATRX_STAGE
path instead of auto-detecting 'test'.
"""

from __future__ import annotations

import pytest

from matrx_utils import (
    MatrxRole,
    MatrxStage,
    RuntimeEnvError,
    get_runtime_env,
    reset_runtime_env_cache,
)


def _clear(monkeypatch) -> None:
    for k in ("MATRX_STAGE", "MATRX_ENV", "MATRX_ROLE", "PYTEST_CURRENT_TEST"):
        monkeypatch.delenv(k, raising=False)
    reset_runtime_env_cache()


def test_prod_app_server_runs_all_daemons(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_STAGE", "production")
    monkeypatch.setenv("MATRX_ROLE", "app_server")
    env = get_runtime_env()
    assert env.stage is MatrxStage.PRODUCTION
    assert env.role is MatrxRole.APP_SERVER
    assert env.runs_scheduler
    assert env.runs_wake_listener
    assert env.runs_auto_ingest_listener
    assert env.strict_startup_gates
    assert not env.dev_login_enabled
    assert not env.allows_insecure_ssl


def test_local_app_server_scheduler_on_shared_bus_daemons_off(monkeypatch):
    # Reproduces today's local .env intent: scheduler on, shared-bus daemons off.
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_STAGE", "local")
    monkeypatch.setenv("MATRX_ROLE", "app_server")
    env = get_runtime_env()
    assert env.runs_scheduler
    assert not env.runs_wake_listener
    assert not env.runs_auto_ingest_listener
    assert env.dev_login_enabled
    assert env.allows_insecure_ssl
    assert not env.strict_startup_gates


def test_worker_and_sandbox_host_run_no_daemons(monkeypatch):
    for role in ("worker", "sandbox_host"):
        _clear(monkeypatch)
        monkeypatch.setenv("MATRX_STAGE", "production")
        monkeypatch.setenv("MATRX_ROLE", role)
        env = get_runtime_env()
        assert not env.runs_scheduler
        assert not env.runs_wake_listener


def test_missing_stage_crashes(monkeypatch):
    _clear(monkeypatch)
    with pytest.raises(RuntimeEnvError):
        get_runtime_env()


def test_unrecognized_stage_crashes(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_STAGE", "staging")
    with pytest.raises(RuntimeEnvError):
        get_runtime_env()


def test_production_without_role_crashes(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_STAGE", "production")
    with pytest.raises(RuntimeEnvError):
        get_runtime_env()


def test_local_without_role_defaults_app_server(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_STAGE", "local")
    env = get_runtime_env()
    assert env.role is MatrxRole.APP_SERVER


def test_legacy_matrx_env_alias_still_resolves(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("MATRX_ENV", "production")
    monkeypatch.setenv("MATRX_ROLE", "app_server")
    env = get_runtime_env()
    assert env.stage is MatrxStage.PRODUCTION


def test_pytest_marker_autodetects_test_stage(monkeypatch):
    # With PYTEST_CURRENT_TEST present (as in any real run), stage is TEST and
    # no MATRX_STAGE is required.
    for k in ("MATRX_STAGE", "MATRX_ENV", "MATRX_ROLE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "x")
    monkeypatch.setenv("MATRX_ROLE", "app_server")
    reset_runtime_env_cache()
    env = get_runtime_env()
    assert env.stage is MatrxStage.TEST
    assert not env.strict_startup_gates


def teardown_module(_module) -> None:
    reset_runtime_env_cache()
