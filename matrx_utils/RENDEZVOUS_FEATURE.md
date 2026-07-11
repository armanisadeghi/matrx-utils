# FEATURE — Rendezvous (order-independent commit ↔ consumer meeting point)

Beside: [`rendezvous.py`](rendezvous.py) · tests: [`../tests/test_rendezvous.py`](../tests/test_rendezvous.py) (30, exhaustive).

## What it kills

A producer makes a keyed resource real (a queued DB INSERT that commits at
end-of-request) and a consumer must act on it (a labeler that UPDATEs that row).
They race. A naive "does it exist yet?" poll is fooled by pending/uncommitted
state and the write hits **zero rows**. Rendezvous removes the race by caching
arrival in **both** directions with a TTL, and gives every held note a **DB
fallback** so a missed announcement still resolves — loudly.

## The two doors

```python
from matrx_utils import rendezvous

# PRODUCER — the resource is COMMITTED and real. Fire on commit, never on queue.
rendezvous.announce(kind, id)

# CONSUMER — run `do` once (kind, id) is committed-present, any arrival order.
rendezvous.on_present(kind, id, do=coro_factory, verify=committed_db_check,
                      ttl=300.0, label="my-work")
```

`do` is a **zero-arg callable returning an awaitable** (a factory, so it's never
"already awaited"). `verify(kind, id) -> bool` is a **COMMITTED** existence read.
Both `announce` and `on_present` are non-blocking and never raise into the caller.

## Resolution matrix (this is the whole contract)

| Situation | Outcome |
|---|---|
| Producer announced first (cache hit) → consumer arrives | run `do` immediately |
| Consumer first → producer announces within `ttl` | run `do` on announce |
| Consumer waits, `ttl` fires, `verify` says row **IS** committed | run `do` **+ YELLOW leak warning** (producer forgot to announce) |
| Consumer waits, `ttl` fires, `verify` says row **NOT** there | drop `do` **+ RED broken-promise alarm** |
| `do` raises | routed to the alarm sink (`error`) — never silent |
| `verify` raises | treated as NOT present (fail closed) → broken-promise |

`stats` (a `RendezvousStats`) counts every path for assertions/telemetry.

## How it's wired in this repo

- **Producer (generic, every table, for free):** `matrx_orm.session.session.flush`
  calls `_announce_committed(coalesced)` the instant a flush transaction
  succeeds — one `announce(model_cls.__name__, pk)` per committed insert/update.
  So "the row exists now" fires from the single authoritative commit point.
- **Consumer (reference):** `matrx_ai.agents.services.conversation_labeler`
  registers `on_present("Conversation", conversation_id, ...)` instead of polling.
  It is scheduled *before* the conversation commits, so order-independence is
  mandatory — the note fires when the end-of-request flush announces the row.

## Invariants / gotchas

- **Announce on COMMIT, never on queue.** A pending-overlay read is exactly the
  bug this replaces. The producer hook lives in `Session.flush`'s success paths.
- **`kind` = `model_cls.__name__`.** Consumers wait on the same name the ORM's
  `DoesNotExist`/errors use (e.g. `"Conversation"`).
- **Presence cache is bounded** (`max_present`, default 50k) and front-purged;
  constant `present_ttl` ⇒ insertion order == expiry order, so eviction is O(expired).
- **Fully injectable for tests** — `now`, `sleep`, `spawn`, `alarm`, `verifier`,
  `autostart_sweeper=False` + drive `sweep(now)` manually. A 5-minute window is
  tested in microseconds with a `FakeClock`; two integration tests exercise the
  real background sweeper on a ~50 ms TTL.
- **Best-effort at the ORM seam:** a rendezvous hiccup must never affect a flush
  that already committed — `_announce_committed` swallows its own exceptions.

## Durable escalation (wired)

The dependency-free default `alarm` is `vcprint` (loud red/yellow). The host
escalates the genuine-failure levels to a durable `system_error` row via
`rendezvous.configure(alarm=...)` in
[`aidream/package_integration.py`](../../../../aidream/package_integration.py)
(`_configure_rendezvous_alarm`): a **BROKEN PROMISE** (`critical`) and a note
whose work/verify **raised** (`error`) both call `matrx_orm.record_error`
(`kind="rendezvous"`). The YELLOW **leak** warning stays terminal-only — that
path DID complete the work, so it's a heads-up, not a lost-work incident.
A standalone consumer (no host) just gets the terminal print.
