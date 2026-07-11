"""Default audit-event logger for matrx-utils file mutations.

Hosts wire this via ``configure_audit_logger(default_audit_logger)``.
Every meaningful file mutation is recorded to the canonical activity log
(``platform.activity_log`` via the ``platform.log_activity`` RPC). The
graveyarded ``cld_events`` outbox is gone in the 2026 DB canonicalization,
so the webhook fan-out path it fed has been retired.

For aidream-specific bridging (Sentry breadcrumbs + the existing
``audit_bridge.py``), hosts can wrap this with their own callable that
calls both.
"""

from __future__ import annotations

import asyncio
from typing import Any

from matrx_utils import vcprint


# High-signal events that get persisted to platform.activity_log.
# Low-signal events (every read, every URL mint) are deliberately
# skipped so the activity log doesn't saturate.
INTERESTING_AUDIT_EVENTS: frozenset[str] = frozenset({
    "file.uploaded",
    "file.replaced",
    "file.deleted",
    "file.hard_deleted",
    "file.restored",
    "file.renamed",
    "file.moved",
    "file.copied",
    "file.version_bumped",
    "file.visibility_changed",
    "asset.uploaded",
    "asset.variants_added",
    "share_link.created",
    "share_link.revoked",
    "share_link.consumed",
    "permission.granted",
    "permission.revoked",
})


def default_audit_logger(event_type: str, payload: dict[str, Any]) -> None:
    """Persist high-signal file mutations to platform.activity_log.

    Designed for ``matrx_utils.conf.configure_audit_logger(...)``. Never
    raises — failure to persist falls through quietly so a file
    operation doesn't fail just because the audit log is unavailable.

    The dispatch is fire-and-forget — we spawn an asyncio task and
    return immediately. Within the task, exceptions are swallowed and
    logged with ``vcprint``.
    """
    if event_type not in INTERESTING_AUDIT_EVENTS:
        return
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_persist(event_type, payload))
        else:
            # Synchronous fallback — run-to-completion. Avoids dropping
            # events in environments where the event loop isn't running
            # yet (eg. host startup).
            asyncio.run(_persist(event_type, payload))
    except Exception as e:
        vcprint(f"[default_audit_logger] dispatch failed: {e!r}", color="yellow")


async def _persist(event_type: str, payload: dict[str, Any]) -> None:
    """Write a single audit row to platform.activity_log via the
    log_activity RPC. Best-effort — never raises out.

    Field mapping (cld_events → platform.activity_log):
      event_type   -> action
      resource_type-> entity_type
      resource_id  -> entity_id
      organization_id -> organization_id
      everything else (+ actor + request_id) -> metadata jsonb

    NOTE: the acting user (payload.user_id) is passed as the explicit
    ``p_actor`` (6-arg log_activity overload) so file events match
    owner-scoped webhooks — the base 5-arg overload stamps auth.uid(),
    which is NULL for the service-role key this layer uses. It is also
    mirrored into metadata.actor_id for consumers of the raw payload.
    """
    try:
        # Resolve the active FileManager via the user's wiring. Hosts
        # call ``configure_settings`` + ``configure_context`` before
        # the first file write, so FileManager.get_instance() is
        # already populated.
        from matrx_utils.file_handling import FileManager
        fm = FileManager.get_instance()
        if fm is None or fm.sync_engine is None:
            return
        client = await fm.sync_engine.db._get_async_client()
        actor_id = payload.get("user_id") or payload.get("actor_id")
        metadata = {
            k: v for k, v in payload.items()
            if k not in (
                "resource_id", "resource_type", "organization_id",
            )
        }
        metadata.setdefault("actor_id", actor_id)
        # activity_log.organization_id is NOT NULL — org-less files belong
        # to the actor's personal org by the platform model.
        org_id = payload.get("organization_id")
        if not org_id and actor_id:
            res = await client.rpc(
                "ensure_personal_organization", {"p_user_id": actor_id}
            ).execute()
            org_id = res.data
        if not org_id:
            vcprint(
                f"[default_audit_logger] dropping {event_type}: no organization and no actor",
                color="yellow",
            )
            return
        await client.schema("platform").rpc(
            "log_activity",
            {
                "p_org": org_id,
                "p_action": event_type,
                "p_entity_type": payload.get("resource_type"),
                "p_entity_id": payload.get("resource_id"),
                "p_metadata": metadata,
                "p_actor": actor_id,
            },
        ).execute()
    except Exception as e:
        vcprint(
            f"[default_audit_logger] log_activity failed: {e!r}", color="yellow"
        )


__all__ = ["default_audit_logger", "INTERESTING_AUDIT_EVENTS"]
