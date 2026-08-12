"""Unit tests for anti-SSRF validation."""

import pytest

from ssrf import SSRFError, validate_url_for_fetch


def test_allows_public_https():
    url = validate_url_for_fetch("https://example.com/path")
    assert url.startswith("https://")


def test_rejects_file_and_data():
    with pytest.raises(SSRFError):
        validate_url_for_fetch("file:///etc/passwd")
    with pytest.raises(SSRFError):
        validate_url_for_fetch("data:text/html,hi")


def test_rejects_localhost_and_local():
    with pytest.raises(SSRFError):
        validate_url_for_fetch("http://localhost/admin")
    with pytest.raises(SSRFError):
        validate_url_for_fetch("http://foo.local/")
    with pytest.raises(SSRFError):
        validate_url_for_fetch("http://127.0.0.1/")


def test_rejects_private_literal_ips():
    for url in (
        "http://10.0.0.1/",
        "http://192.168.1.1/",
        "http://172.16.0.5/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
    ):
        with pytest.raises(SSRFError):
            validate_url_for_fetch(url)


def test_rejects_non_http_schemes():
    with pytest.raises(SSRFError):
        validate_url_for_fetch("ftp://example.com/")
    with pytest.raises(SSRFError):
        validate_url_for_fetch("example.com/no-scheme")
