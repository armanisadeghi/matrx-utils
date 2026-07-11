"""Pytest configuration for matrx-utils tests.

``cloud_sync_test.py`` is a manual, live-credential integration script (it talks
to real AWS S3 + Supabase using ``DEVELOPER_USER_ID`` from ``.env`` and is meant
to be run with ``python tests/cloud_sync_test.py``). Its ``test_*`` functions
take an ``engine`` argument that pytest would try — and fail — to resolve as a
fixture. It is intentionally excluded from automated collection so the unit
suite stays green without cloud credentials; run it by hand when validating the
cloud-sync round-trip.
"""

collect_ignore = ["cloud_sync_test.py"]
