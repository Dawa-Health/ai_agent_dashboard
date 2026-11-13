import json

import pytest

import app as app_module
from fakes import FakeResponse


def test_parse_json_value():
    assert app_module.parse_json_value(None) is None
    assert app_module.parse_json_value({"a": 1}) == {"a": 1}
    assert app_module.parse_json_value(5) is None
    assert app_module.parse_json_value("not json") is None
    assert app_module.parse_json_value('{"a": 1}') == {"a": 1}


@pytest.mark.parametrize("text,expected", [
    ("Poster 1 - Avondale", "Poster 1"),
    ("poster2", "Poster 2"),
    ("FLYER", "Flyer"),
    ("billboard", None),
    (None, None),
])
def test_detect_source_type(text, expected):
    assert app_module.detect_source_type(text) == expected


def test_detect_clinic():
    assert app_module.detect_clinic("Avondale Clinic poster 1", {}) == "Avondale Clinic"
    assert app_module.detect_clinic("x", {"clinic_name": "chelstone clinic"}) == "Chelstone Clinic"
    assert app_module.detect_clinic("nothing here", {}) is None


def test_scan_redis_keys_follows_cursor_and_dedupes(install_requests):
    pages = {
        "0": {"result": ["7", ["referrals:1", "referrals:2"]]},
        "7": {"result": ["0", ["referrals:2", "referrals:3"]]},
    }
    install_requests(get=lambda url, **kw: FakeResponse(pages[url.rsplit("/", 1)[-1]]))
    assert app_module.scan_redis_keys("referrals*") == [
        "referrals:1", "referrals:2", "referrals:3"]


def test_read_redis_values_empty():
    assert app_module.read_redis_values([]) == {}


def test_read_redis_values_pipeline(install_requests):
    install_requests(post=lambda url, **kw: FakeResponse(
        [{"result": '{"a": 1}'}, {"result": None}]))
    assert app_module.read_redis_values(["k1", "k2"]) == {"k1": '{"a": 1}', "k2": None}


def test_read_redis_values_falls_back_to_single_gets(install_requests):
    def boom(url, **kw):
        raise RuntimeError("pipeline down")
    install_requests(get=lambda url, **kw: FakeResponse({"result": "v"}), post=boom)
    assert app_module.read_redis_values(["k1", "k2"]) == {"k1": "v", "k2": "v"}


def test_build_with_no_keys(monkeypatch):
    monkeypatch.setattr(app_module, "scan_redis_keys", lambda pattern: [])
    out = app_module.build_qr_analytics(force_refresh=True)
    assert out["ok"] is True
    assert out["totalRecords"] == 0
    assert out["cached"] is False


def _fake_records(monkeypatch):
    records = {
        "referrals:1": json.dumps({"source": "Avondale Clinic Poster 1"}),
        "referrals:2": json.dumps({"source": "Chelstone Clinic flyer"}),
        "referrals:3": "garbage",
        "referrals:4": json.dumps({"source": "unknown place"}),
    }
    calls = {"scan": 0}

    def scan(pattern):
        calls["scan"] += 1
        return list(records)

    monkeypatch.setattr(app_module, "scan_redis_keys", scan)
    monkeypatch.setattr(app_module, "read_redis_values", lambda keys: records)
    return calls


def test_build_counts_matched_valid_and_malformed(monkeypatch):
    _fake_records(monkeypatch)
    out = app_module.build_qr_analytics(force_refresh=True)
    assert out["totalRecords"] == 4
    assert out["validRecords"] == 3
    assert out["malformedRecords"] == 1
    assert out["matchedRecords"] == 2
    assert out["counts"]["Avondale Clinic"]["Poster 1"] == 1
    assert out["counts"]["Chelstone Clinic"]["Flyer"] == 1


def test_second_call_uses_cache_until_refresh_forced(monkeypatch):
    calls = _fake_records(monkeypatch)
    app_module.build_qr_analytics(force_refresh=True)
    cached = app_module.build_qr_analytics()
    assert cached["cached"] is True
    assert calls["scan"] == 1
    app_module.build_qr_analytics(force_refresh=True)
    assert calls["scan"] == 2


def test_route_returns_payload(client, monkeypatch):
    _fake_records(monkeypatch)
    body = client.get("/api/qr-analytics?refresh=1").get_json()
    assert body["ok"] is True and body["matchedRecords"] == 2


def test_route_degrades_to_zero_counts_on_upstream_error(client, monkeypatch):
    def boom(pattern):
        raise RuntimeError("redis down")
    monkeypatch.setattr(app_module, "scan_redis_keys", boom)
    resp = client.get("/api/qr-analytics?refresh=1")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["ok"] is False
    assert body["totalRecords"] == 0
