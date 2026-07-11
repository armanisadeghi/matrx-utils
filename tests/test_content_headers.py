"""Regression tests for the Content-Type / Content-Disposition write contract.

The bug these lock down: cloud objects were written with NO ContentType, so
S3 stored them as ``binary/octet-stream`` and bare public CDN URLs downloaded
instead of rendering. Every S3 PUT path must now stamp a definitive
ContentType + a policy-correct ContentDisposition, sourced from the one
``resolve_object_headers`` SSOT.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from matrx_utils.file_handling.content_headers import (
    ObjectHeaders,
    resolve_object_headers,
    sniffed_content_type,
)
from matrx_utils.file_handling.backends.s3_backend import S3Backend


# --------------------------------------------------------------------------
# Policy SSOT — resolve_object_headers
# --------------------------------------------------------------------------

def test_declared_mime_on_extensionless_key_is_authoritative():
    # The canonical org-logo case: key is <owner>/<file_id> (no extension),
    # so the declared mime is the ONLY source. Must NOT be octet-stream.
    h = resolve_object_headers(mime_type="image/png", file_name="4cf62e4e/b093954c")
    assert h == ObjectHeaders(content_type="image/png", content_disposition="inline")


def test_guess_from_extension_when_no_declared_mime():
    h = resolve_object_headers(mime_type=None, file_name="logo/v/logo_lg.png")
    assert h.content_type == "image/png"
    assert h.content_disposition == "inline"


def test_pdf_is_inline():
    h = resolve_object_headers(mime_type="application/pdf", file_name="x")
    assert h.content_disposition == "inline"


def test_dangerous_svg_is_coerced_to_attachment():
    # SVG can carry script — stored-XSS guard forces octet-stream + attachment.
    h = resolve_object_headers(mime_type="image/svg+xml", file_name="logo.svg")
    assert h.content_type == "application/octet-stream"
    assert h.content_disposition == "attachment"


def test_dangerous_html_is_coerced_to_attachment():
    h = resolve_object_headers(mime_type="text/html", file_name="page.html")
    assert h.content_type == "application/octet-stream"
    assert h.content_disposition == "attachment"


def test_unknown_bytes_fall_back_to_octet_attachment():
    h = resolve_object_headers(mime_type=None, file_name="blob")
    assert h.content_type == "application/octet-stream"
    assert h.content_disposition == "attachment"


def test_non_renderable_known_type_is_attachment():
    h = resolve_object_headers(mime_type="application/zip", file_name="a.zip")
    assert h.content_type == "application/zip"
    assert h.content_disposition == "attachment"


def test_read_side_policy_shares_the_same_decision():
    # download_stream re-exports this; write + read must agree.
    ct, force_attach = sniffed_content_type(
        {"mime_type": "image/png", "file_name": "a.png"}, allow_inline=True
    )
    assert ct == "image/png"
    assert force_attach is False


# --------------------------------------------------------------------------
# S3Backend stamps the headers on every PUT path
# --------------------------------------------------------------------------

def _fake_s3() -> S3Backend:
    b = S3Backend.__new__(S3Backend)  # bypass __init__ (no creds needed)
    b._client = MagicMock()
    b._configured = True
    b._default_bucket = "cdn.matrxserver.com"
    b._region = "us-east-1"
    return b


def test_write_stamps_content_type_and_inline_disposition():
    b = _fake_s3()
    b.write("cdn.matrxserver.com/owner/fileid", b"\x89PNG data", content_type="image/png")
    b._client.put_object.assert_called_once()
    kw = b._client.put_object.call_args.kwargs
    assert kw["ContentType"] == "image/png"
    assert kw["ContentDisposition"] == "inline"


def test_write_without_content_type_never_emits_octet_for_known_extension():
    b = _fake_s3()
    b.write("cdn.matrxserver.com/owner/logo.png", b"data")  # no content_type kwarg
    kw = b._client.put_object.call_args.kwargs
    assert kw["ContentType"] == "image/png"


def test_multipart_upload_stamps_content_type():
    b = _fake_s3()
    b._client.create_multipart_upload.return_value = {"UploadId": "uid"}
    b._client.upload_part.return_value = {"ETag": "etag"}
    headers = resolve_object_headers(mime_type="image/png", file_name="key")
    b._multipart_upload(b._client, "cdn.matrxserver.com", "owner/fileid", b"x" * 16, None, headers)
    kw = b._client.create_multipart_upload.call_args.kwargs
    assert kw["ContentType"] == "image/png"
    assert kw["ContentDisposition"] == "inline"


def test_restamp_headers_uses_copy_object_replace():
    b = _fake_s3()
    ok = b.restamp_headers(
        "cdn.matrxserver.com/owner/fileid",
        content_type="image/png",
        content_disposition="inline",
    )
    assert ok is True
    b._client.copy_object.assert_called_once()
    kw = b._client.copy_object.call_args.kwargs
    assert kw["MetadataDirective"] == "REPLACE"
    assert kw["ContentType"] == "image/png"
    assert kw["ContentDisposition"] == "inline"
    assert kw["CopySource"] == {"Bucket": "cdn.matrxserver.com", "Key": "owner/fileid"}
