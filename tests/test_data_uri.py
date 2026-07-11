"""Level 1: matrx_utils.data_uri — encode / decode / detect / strip."""
import base64

import pytest

from matrx_utils import decode_data_uri, encode_data_uri, is_data_uri, strip_data_uri


def test_encode_then_decode_round_trips():
    data = b"\x89PNG\r\n\x1a\n binary"
    uri = encode_data_uri(data, "image/png")
    assert uri.startswith("data:image/png;base64,")
    decoded, mime = decode_data_uri(uri)
    assert decoded == data and mime == "image/png"


def test_is_data_uri():
    assert is_data_uri("data:image/png;base64,AAAA")
    assert is_data_uri("data:text/plain,hello")
    assert not is_data_uri("https://example.com/x.png")
    assert not is_data_uri("AAAA")          # bare base64 is not a data URI
    assert not is_data_uri(b"data:x,y")     # bytes, not str


def test_decode_percent_encoded_form():
    data, mime = decode_data_uri("data:text/plain,hello%20world")
    assert data == b"hello world" and mime == "text/plain"


def test_decode_drops_charset_and_handles_absent_mime():
    data, mime = decode_data_uri("data:text/plain;charset=utf-8;base64," + base64.b64encode(b"hi").decode())
    assert data == b"hi" and mime == "text/plain"
    # absent mediatype -> None
    data2, mime2 = decode_data_uri("data:;base64," + base64.b64encode(b"x").decode())
    assert data2 == b"x" and mime2 is None


def test_decode_rejects_non_data_uri_and_missing_comma():
    with pytest.raises(ValueError):
        decode_data_uri("https://example.com/x")
    with pytest.raises(ValueError):
        decode_data_uri("data:image/png;base64")  # no comma


def test_strip_data_uri_returns_payload_or_passthrough():
    assert strip_data_uri("data:image/png;base64,QUJD") == "QUJD"
    assert strip_data_uri("QUJD") == "QUJD"          # bare base64 unchanged
    assert strip_data_uri("data:text/plain,hi") == "hi"
