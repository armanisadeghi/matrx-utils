"""Single source of truth for *what kind of host am I, and which code line is this?*

Two orthogonal axes, each a small closed enum, resolved ONCE per process and
cached. EVERY behavior decision that used to hide behind an ad-hoc
``os.getenv("SOME_FLAG")`` reads a **named property** here instead.

------------------------------------------------------------------------------
The two axes (why two, not one)
------------------------------------------------------------------------------
``MATRX_STAGE`` and ``MATRX_ROLE`` answer DIFFERENT questions. Smashing them
into one enum is what created the fog ("is a sandbox production?" — yes *and*
it's a sandbox) and made coding agents invent scattered flags. Keep them apart.

``MATRX_STAGE`` — *which code line is this, and how much do we trust it?*
    production    the official, live code. The prod brain, the sandbox
                  containers, AND the EC2 sandbox-host ALL run PRODUCTION code.
    development   experimental servers running not-yet-released code.
    local         a developer's own machine.
    test          a pytest run. Auto-detected — never set this by hand.

``MATRX_ROLE`` — *what is THIS process's job?*
    app_server    the brain: serves the main API. The singleton that runs the
                  scheduler scanner / cloud-file webhook dispatcher / wake
                  listener. This is also what you run locally (``python run.py``).
    worker        background workflow-job drainer + cron watcher (separate
                  process: ``python -m aidream.api.workflow_worker``).
    sandbox       aidream running INSIDE a sandbox container — the container IS
                  the user/project boundary. Auto-detected via a marker file.
    sandbox_host  the EC2 box that provisions and serves sandbox containers.

A sandbox runs ``stage=production`` code (trust) but is ``role=sandbox`` (job).
The two never collapse.

------------------------------------------------------------------------------
The contract (this is the whole point)
------------------------------------------------------------------------------
* NOTHING branches on a hand-rolled ``os.getenv(...)`` for host identity or for
  turning a feature on/off. Ask :func:`get_runtime_env` and read a property.
* A behavior that genuinely differs per environment → add a property HERE.
* A behavior we just want toggleable while testing a fix → a ``CAPS`` constant
  at the top of the owning file (code-reviewed, shipped via git), NOT an env
  var. A code push is the correct "deploy" for a behavior change.
* Env vars are for SECRETS and for these two declared axes ONLY.

------------------------------------------------------------------------------
Failure is LOUD, never silent
------------------------------------------------------------------------------
* ``MATRX_STAGE`` missing or unrecognized → the process CRASHES at first
  resolution with a red banner. No silent ``"local"`` default ever again.
* ``MATRX_ROLE`` missing on a ``production`` stage → CRASH (the EC2 box can
  never silently mis-role and fight the prod brain over shared state).
* ``MATRX_ROLE`` missing on local/dev → defaults to ``app_server`` with a loud
  warning so a developer machine never breaks but the default is visible.
"""

from __future__ import annotations

import os
from enum import Enum

from matrx_utils.fancy_prints import vcprint

# Legacy name accepted for one migration window. Set MATRX_STAGE and delete this.
_LEGACY_STAGE_ENV = "MATRX_ENV"
_STAGE_ENV = "MATRX_STAGE"
_ROLE_ENV = "MATRX_ROLE"

# The directory ONLY the ``matrx-sandbox:aidream`` image bakes in. Its presence
# is an unambiguous, env-free signal that we are inside a sandbox container.
_SANDBOX_MARKER = "/opt/aidream-template"


class MatrxStage(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    LOCAL = "local"
    TEST = "test"


class MatrxRole(Enum):
    APP_SERVER = "app_server"
    WORKER = "worker"
    SANDBOX = "sandbox"
    SANDBOX_HOST = "sandbox_host"


# Accepted spellings → enum. Generous on input, exact on storage.
_STAGE_ALIASES: dict[str, MatrxStage] = {
    "production": MatrxStage.PRODUCTION,
    "prod": MatrxStage.PRODUCTION,
    "development": MatrxStage.DEVELOPMENT,
    "dev": MatrxStage.DEVELOPMENT,
    "local": MatrxStage.LOCAL,
    "localhost": MatrxStage.LOCAL,
    "test": MatrxStage.TEST,
    "testing": MatrxStage.TEST,
    "ci": MatrxStage.TEST,
}

_ROLE_ALIASES: dict[str, MatrxRole] = {
    "app_server": MatrxRole.APP_SERVER,
    "app": MatrxRole.APP_SERVER,
    "server": MatrxRole.APP_SERVER,
    "brain": MatrxRole.APP_SERVER,
    "worker": MatrxRole.WORKER,
    "sandbox": MatrxRole.SANDBOX,
    "sandbox_host": MatrxRole.SANDBOX_HOST,
    "sandbox-host": MatrxRole.SANDBOX_HOST,
    "sandboxhost": MatrxRole.SANDBOX_HOST,
}


class RuntimeEnvError(RuntimeError):
    """Raised at startup when the runtime environment cannot be resolved.

    This is a deliberate fail-loud gate, not a real bug — a server was started
    without declaring MATRX_STAGE / MATRX_ROLE. The fix is a deployment config
    change, named in the message.
    """


class RuntimeEnv:
    """Resolved host identity. Construct via :func:`get_runtime_env`."""

    __slots__ = ("stage", "role")

    def __init__(self, stage: MatrxStage, role: MatrxRole) -> None:
        self.stage = stage
        self.role = role

    # ----- stage axis -------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.stage is MatrxStage.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.stage is MatrxStage.DEVELOPMENT

    @property
    def is_local(self) -> bool:
        return self.stage is MatrxStage.LOCAL

    @property
    def is_test(self) -> bool:
        return self.stage is MatrxStage.TEST

    @property
    def is_real_deployment(self) -> bool:
        """A shared server (prod or dev), not a laptop or a test run. The line
        below which loud safety gates (strict schema, etc.) engage."""
        return self.stage in (MatrxStage.PRODUCTION, MatrxStage.DEVELOPMENT)

    # ----- role axis --------------------------------------------------------
    @property
    def is_app_server(self) -> bool:
        return self.role is MatrxRole.APP_SERVER

    @property
    def is_worker(self) -> bool:
        return self.role is MatrxRole.WORKER

    @property
    def is_sandbox(self) -> bool:
        return self.role is MatrxRole.SANDBOX

    @property
    def is_sandbox_host(self) -> bool:
        return self.role is MatrxRole.SANDBOX_HOST

    # ----- derived behavior (replaces the old scattered flags) --------------
    # Each property below names a flag we DELETED. The mapping is the spec.
    @property
    def runs_scheduler(self) -> bool:
        """Replaces AIDREAM_SCHEDULER. The app_server is the canonical scanner
        host — including locally, so scheduling can be exercised in dev."""
        return self.is_app_server

    @property
    def runs_wake_listener(self) -> bool:
        """Replaces AIDREAM_CROSS_COMPONENT_WAKE_ENABLED. Same shared-bus
        reasoning as the dispatcher: production brain only."""
        return self.is_app_server and self.is_production

    @property
    def runs_auto_ingest_listener(self) -> bool:
        """Replaces AIDREAM_AUTO_INGEST_LISTENER. LISTENs on a SHARED Postgres
        NOTIFY channel and dispatches ingestion; only the production brain may
        run it, else a laptop/dev process double-ingests production writes."""
        return self.is_app_server and self.is_production

    @property
    def runs_suggestion_sweep_listener(self) -> bool:
        """The post-processing suggestion-sweep listener. LISTENs on a SHARED
        Postgres NOTIFY channel ('suggestion_sweep') and drains the shared
        kg_sweep_queue; only the production brain may run it. The per-group
        advisory lock makes a second process harmless, but we still gate to one
        host for clean ownership — same reasoning as the auto-ingest listener."""
        return self.is_app_server and self.is_production

    @property
    def runs_file_rag_sweeper(self) -> bool:
        """Drains the cld_file_rag_jobs queue (scheduled auto-RAG on file
        upload) and dispatches ingestion. Mirrors ``runs_scheduler`` (NOT the
        NOTIFY listener): the app_server runs it EVERYWHERE — including locally
        — so the scheduled path can be exercised in dev. The per-row CAS claim
        makes the shared queue exactly-once across hosts (whoever claims a job
        wins; a crashed run is recovered by the 30-min watchdog → abandoned),
        so a second sweeping process can never double-run a file. Sandboxes and
        workers never sweep."""
        return self.is_app_server

    @property
    def runs_runtime_reaper(self) -> bool:
        """The matrx-runtime crash-recovery reaper sweeps SHARED runtime.global_execution
        rows (fails any leased execution whose worker died). The terminal-write CAS makes
        a second reaper harmless, but — like the cld dispatcher / NOTIFY listeners — we
        gate to ONE host for clean ownership and so a laptop on the shared DB never reaps
        production executions. Production brain only."""
        return self.is_app_server and self.is_production

    @property
    def dev_login_enabled(self) -> bool:
        """Replaces ENABLE_DEV_LOGIN. The JWT-minting dev-login endpoint mounts
        only on a developer machine or a dev server — NEVER production, never a
        sandbox. (The DEV_LOGIN_SECRET secret is checked separately.)"""
        return self.role is MatrxRole.APP_SERVER and self.stage in (
            MatrxStage.LOCAL,
            MatrxStage.DEVELOPMENT,
        )

    @property
    def strict_startup_gates(self) -> bool:
        """Replaces AIDREAM_STRICT_SCHEMA / AIDREAM_STRICT_SKILLS. Schema-drift
        and skill→tool validation FAIL BOOT on a real deployment (loud), and
        only warn on a laptop / test run (where intentional drift is normal)."""
        return self.is_real_deployment

    @property
    def allows_insecure_ssl(self) -> bool:
        """Replaces FASTINO_INSECURE_SSL / GLINER2_INSECURE_SSL. TLS verification
        may be skipped ONLY on a developer machine. A real deployment (prod, dev
        server, sandbox, EC2 host) MUST verify certificates."""
        return self.is_local

    @property
    def verbose_observability_default(self) -> bool:
        """Default for chatty AI-call / tool previews: on for a laptop, off on a
        shared server. An explicit debug knob may still override per call."""
        return self.is_local

    def __repr__(self) -> str:
        return f"RuntimeEnv(stage={self.stage.value!r}, role={self.role.value!r})"


_RESOLVED: RuntimeEnv | None = None


def _in_sandbox() -> bool:
    # The sandbox image bakes in this dir — an env-free, unspoofable signal.
    return os.path.isdir(_SANDBOX_MARKER)


def _resolve_stage() -> MatrxStage:
    # pytest sets this for the duration of every test — auto-detect so test runs
    # never need to declare a stage and never accidentally look like prod.
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return MatrxStage.TEST

    raw = (os.environ.get(_STAGE_ENV) or "").strip().lower()
    legacy_used = False
    if not raw:
        legacy = (os.environ.get(_LEGACY_STAGE_ENV) or "").strip().lower()
        if legacy:
            raw = legacy
            legacy_used = True

    if not raw:
        # A sandbox container runs the official, released code — so it IS the
        # production stage. Auto-inferred from the marker so sandbox images need
        # ZERO env (an explicit MATRX_STAGE still wins, e.g. a dev-code sandbox).
        if _in_sandbox():
            return MatrxStage.PRODUCTION
        _crash(
            f"{_STAGE_ENV} is not set.",
            "Set it to exactly one of: production | development | local "
            "(a pytest run is auto-detected as 'test').",
        )

    stage = _STAGE_ALIASES.get(raw)
    if stage is None:
        _crash(
            f"{_STAGE_ENV}={raw!r} is not a recognized stage.",
            "Valid values: production | development | local.",
        )

    if legacy_used:
        vcprint(
            f"[runtime_env] {_LEGACY_STAGE_ENV} is DEPRECATED — read as "
            f"{_STAGE_ENV}={stage.value!r}. Rename it to {_STAGE_ENV} on this "
            "host; the legacy alias will be removed.",
            color="yellow",
        )
    return stage


def _resolve_role(stage: MatrxStage) -> MatrxRole:
    if _in_sandbox():
        return MatrxRole.SANDBOX

    raw = (os.environ.get(_ROLE_ENV) or "").strip().lower()
    if raw:
        role = _ROLE_ALIASES.get(raw)
        if role is None:
            _crash(
                f"{_ROLE_ENV}={raw!r} is not a recognized role.",
                "Valid values: app_server | worker | sandbox | sandbox_host.",
            )
        return role

    # Unset. On a real production host this is dangerous (a mis-roled box would
    # start the singleton daemons and fight the brain), so crash. On a laptop /
    # dev server, default to the brain but say so loudly.
    if stage is MatrxStage.PRODUCTION:
        _crash(
            f"{_ROLE_ENV} is not set on a PRODUCTION host.",
            "Production processes MUST declare their role: "
            "app_server | worker | sandbox | sandbox_host.",
        )

    vcprint(
        f"[runtime_env] {_ROLE_ENV} not set on stage={stage.value!r}; defaulting "
        f"to role={MatrxRole.APP_SERVER.value!r}. Set {_ROLE_ENV} to silence this.",
        color="yellow",
    )
    return MatrxRole.APP_SERVER


def _crash(headline: str, fix: str) -> None:
    banner = (
        "\n"
        "############################################################################\n"
        "##  RUNTIME ENVIRONMENT NOT RESOLVED — startup aborted.                    ##\n"
        "############################################################################\n"
        f"##  {headline}\n"
        f"##  FIX: {fix}\n"
        "##\n"
        "##  These two variables are the ONLY way this codebase learns what kind\n"
        "##  of host it is. They are required by design so a misconfigured server\n"
        "##  fails LOUDLY here instead of silently running the wrong code path.\n"
        "############################################################################"
    )
    vcprint(banner, color="red")
    raise RuntimeEnvError(f"{headline} {fix}")


def get_runtime_env() -> RuntimeEnv:
    """Resolve (once) and return this process's :class:`RuntimeEnv`.

    Raises :class:`RuntimeEnvError` at first call if MATRX_STAGE (or, on a
    production stage, MATRX_ROLE) is missing or invalid.
    """
    global _RESOLVED
    if _RESOLVED is None:
        stage = _resolve_stage()
        role = _resolve_role(stage)
        _RESOLVED = RuntimeEnv(stage, role)
    return _RESOLVED


def reset_runtime_env_cache() -> None:
    """Drop the cached resolution. For tests that manipulate the env only."""
    global _RESOLVED
    _RESOLVED = None
