"""Safety logic of the S3⟷DB reconciler (scripts/reconcile_orphan_objects.py).

This tool DELETES objects. Every function here decides whether a real user file
lives or dies, so each one is pinned against the specific way it can kill data:

  ReferenceExtractor  — a reference it fails to parse is a file it fails to
                        claim, i.e. a file it deletes.
  _norm_key           — a link it fails to make downgrades a SOLE COPY into the
                        class that gets purged.
  _classify           — must FAIL SAFE: unsure => keep.
  _unmanaged_reason   — row-less-by-design prefixes (Image Studio staging) must
                        never be touched; "no row" is their normal state.

The script lives in scripts/ (not a package), so it is loaded by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parents[3] / "scripts" / "reconcile_orphan_objects.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("_reconcile", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rec = _load()
BUCKETS = {"matrx-user-files", "cdn.matrxserver.com"}


@pytest.fixture()
def ex():
    return rec.ReferenceExtractor(set(BUCKETS))


# ---------------------------------------------------------------------------
# ReferenceExtractor — every shape a reference is persisted in
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("s3://matrx-user-files/o/f", "matrx-user-files/o/f"),
        # CDN: the public bucket is NAMED for its host.
        ("https://cdn.matrxserver.com/o/pic.png", "cdn.matrxserver.com/o/pic.png"),
        # Virtual-hosted + path-style + presigned (query stripped).
        ("https://matrx-user-files.s3.amazonaws.com/o/f", "matrx-user-files/o/f"),
        ("https://matrx-user-files.s3.us-east-1.amazonaws.com/o/f", "matrx-user-files/o/f"),
        ("https://s3.us-east-1.amazonaws.com/matrx-user-files/o/f", "matrx-user-files/o/f"),
        ("https://matrx-user-files.s3.amazonaws.com/o/f?X-Amz-Signature=abc", "matrx-user-files/o/f"),
        # Percent-encoding: S3 lists the RAW key, so a %20 that stays encoded
        # matches nothing -> the live file looks orphaned -> deleted.
        ("https://cdn.matrxserver.com/o/My%20File.png", "cdn.matrxserver.com/o/My File.png"),
        # An s3:// key has no query string — a literal '?' belongs to the key.
        ("s3://matrx-user-files/o/what?.png", "matrx-user-files/o/what?.png"),
        # Foreign hosts are NOT a claim on our storage.
        ("https://example.com/o/f", None),
        ("https://other-bucket.s3.amazonaws.com/o/f", None),
        ("", None),
        (None, None),
    ],
)
def test_extract(ex, value, expected):
    assert ex.extract(value) == expected


def test_extract_all_keeps_keys_containing_spaces(ex):
    """Our paths contain spaces ("Inside Matters/DSC09357.jpg"). Stopping the
    token at the first space truncates the key -> the object looks unclaimed
    -> a live user photo is deleted."""
    text = 'see https://cdn.matrxserver.com/o/Inside Matters/DSC09357.jpg for the pic'
    assert "cdn.matrxserver.com/o/Inside Matters/DSC09357.jpg" in ex.extract_all(text)


def test_extract_all_finds_unicode_refs_in_jsonb(ex):
    """json.dumps defaults to ensure_ascii=True, which would turn 'Café' into
    'Caf\\u00e9' and leave the REAL object unclaimed."""
    blob = {"src": "https://cdn.matrxserver.com/o/Café/photo.jpg"}
    assert "cdn.matrxserver.com/o/Café/photo.jpg" in ex.extract_all(blob)


def test_extract_all_finds_every_ref_in_one_blob(ex):
    blob = {"a": "s3://matrx-user-files/o/1", "b": ["https://cdn.matrxserver.com/o/2"]}
    assert ex.extract_all(blob) == {"matrx-user-files/o/1", "cdn.matrxserver.com/o/2"}


# ---------------------------------------------------------------------------
# _norm_key — a missed link downgrades a sole copy into the purged class
# ---------------------------------------------------------------------------


def test_norm_key_unifies_unicode_forms():
    """macOS uploads NFD filenames; Postgres stores what it was handed. If the
    two sides normalize differently the link MISSES — and a missed link puts a
    SOLE COPY into the class we delete. Both forms are built explicitly so an
    editor normalizing this source file cannot silently neuter the test.
    """
    import unicodedata

    nfc = unicodedata.normalize("NFC", "Caf\u00e9/photo.jpg")   # precomposed e-acute
    nfd = unicodedata.normalize("NFD", nfc)                     # e + combining acute
    assert nfd != nfc, "precondition: the two encodings differ byte-wise"
    assert rec._norm_key(nfd) == rec._norm_key(nfc)


def test_norm_key_decodes_percent_encoding():
    assert rec._norm_key("My%20File.png") == "My File.png"


# ---------------------------------------------------------------------------
# _classify — unsure MUST mean keep
# ---------------------------------------------------------------------------

OWNER = "11111111-1111-1111-1111-111111111111"
FILE_ID = "22222222-2222-2222-2222-222222222222"
ROW_URI = f"s3://matrx-user-files/{OWNER}/{FILE_ID}"
ROW_PATH = f"matrx-user-files/{OWNER}/{FILE_ID}"
PATH_KEY = f"matrx-user-files/{OWNER}/Inside Matters/DSC.jpg"


def test_stale_duplicate_only_when_the_rows_own_object_exists(ex):
    """The row's bytes are safe at the file_id key -> the path-derived copy is
    pure waste."""
    idx = {(OWNER, "Inside Matters/DSC.jpg"): ROW_URI}
    got = rec._classify(PATH_KEY, idx, {ROW_PATH}, ex, set())
    assert got == "stale_rekey_duplicate"


def test_sole_copy_when_the_rows_own_object_is_missing(ex):
    """Row points at an object that does NOT exist -> this 'orphan' is the file's
    ONLY surviving copy. Purging it destroys the file."""
    idx = {(OWNER, "Inside Matters/DSC.jpg"): ROW_URI}
    got = rec._classify(PATH_KEY, idx, set(), ex, set())  # row's object absent
    assert got == "recoverable_sole_copy"


def test_unlinkable_object_of_an_owner_with_broken_files_is_kept(ex):
    """FAIL-SAFE: we could not link it, and this owner HAS a row pointing at a
    missing object — the link may have missed. Refuse to purge rather than guess."""
    got = rec._classify(PATH_KEY, {}, set(), ex, {OWNER})
    assert got == "recoverable_sole_copy"


def test_unlinkable_object_of_a_healthy_owner_is_unreferenced(ex):
    got = rec._classify(PATH_KEY, {}, set(), ex, set())
    assert got == "unreferenced"


# ---------------------------------------------------------------------------
# _unmanaged_reason — row-less BY DESIGN, never purgeable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    [
        "staged-variants/user/job/preset.png",  # Image Studio: bucket-root prefix
        f"{OWNER}/system-files/previews/x.png",  # under an owner segment
        "opinions/0001/5.json.zst",  # derived key, rows in a separate DB
    ],
)
def test_unmanaged_prefixes_are_protected(key):
    assert rec._unmanaged_reason(key) is not None


@pytest.mark.parametrize(
    "key",
    [f"{OWNER}/Inbox/a.pdf", f"{OWNER}/{FILE_ID}", ".versions/f/v1/thumb.jpg"],
)
def test_normal_keys_are_reconcilable(key):
    assert rec._unmanaged_reason(key) is None
