import pytest

import app as app_module
from fakes import FakeResponse


def wa_payload(message):
    return {"object": "whatsapp_business_account",
            "entry": [{"changes": [{"field": "messages",
                                    "value": {"messages": [message]}}]}]}


def test_webhook_verification_accepts_correct_token(client, monkeypatch):
    monkeypatch.setattr(app_module, "VERIFY_TOKEN", "test-token")
    r = client.get("/webhook", query_string={
        "hub.mode": "subscribe", "hub.verify_token": "test-token", "hub.challenge": "abc"})
    assert (r.status_code, r.get_data(as_text=True)) == (200, "abc")


def test_webhook_verification_rejects_wrong_or_missing_token(client, monkeypatch):
    monkeypatch.setattr(app_module, "VERIFY_TOKEN", "test-token")
    wrong = client.get("/webhook", query_string={
        "hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "abc"})
    missing = client.get("/webhook")
    assert wrong.status_code == 403 and missing.status_code == 403


def test_webhook_verification_rejects_when_token_not_configured(client, monkeypatch):
    monkeypatch.setattr(app_module, "VERIFY_TOKEN", "")
    r = client.get("/webhook", query_string={
        "hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "abc"})
    assert r.status_code == 403


@pytest.mark.parametrize("message", [
    {"from": "263771234567", "type": "text", "text": {"body": "hello"}},
    {"from": "263771234567", "type": "interactive",
     "interactive": {"type": "button_reply", "button_reply": {"title": "Yes"}}},
    {"from": "263771234567", "type": "interactive",
     "interactive": {"type": "list_reply", "list_reply": {"title": "Option A"}}},
    {"from": "263771234567", "type": "image", "image": {"id": "img-1"}},
])
def test_webhook_accepts_each_message_type(client, message):
    r = client.post("/webhook", json=wa_payload(message))
    assert r.status_code == 200 and r.get_json()["status"] == "success"


def test_webhook_ignores_other_objects(client):
    assert client.post("/webhook", json={"object": "page"}).status_code == 200


def test_webhook_rejects_non_object_body(client):
    r = client.post("/webhook", data="null", content_type="application/json")
    assert r.status_code == 400


def test_send_success_builds_correct_request(client, install_requests, monkeypatch):
    monkeypatch.setattr(app_module, "WHATSAPP_TOKEN", "test-token")
    fake = install_requests(post=lambda url, **kw: FakeResponse({"messages": [{"id": "x"}]}))
    r = client.post("/sendWhatsApp", json={"to": "263771234567", "message": "hi"})
    assert r.status_code == 200 and r.get_json()["status"] == "sent"
    _, url, kw = fake.calls[0]
    assert kw["json"]["to"] == "263771234567"
    assert kw["json"]["text"]["body"] == "hi"
    assert kw["headers"]["Authorization"] == "Bearer test-token"
    assert kw["timeout"]


def test_send_passes_upstream_error_status_through(client, install_requests):
    install_requests(post=lambda url, **kw: FakeResponse({"error": {"message": "bad"}}, 400))
    r = client.post("/sendWhatsApp", json={"to": "1", "message": "hi"})
    assert r.status_code == 400 and r.get_json()["status"] == "error"


@pytest.mark.parametrize("body", [{}, {"to": "1"}, {"message": "hi"}])
def test_send_rejects_missing_fields_without_calling_whatsapp(client, install_requests, body):
    fake = install_requests(post=lambda url, **kw: FakeResponse({}))
    assert client.post("/sendWhatsApp", json=body).status_code == 400
    assert fake.calls == []


def test_send_returns_502_when_whatsapp_unreachable(client, install_requests):
    def boom(url, **kw):
        raise RuntimeError("down")
    install_requests(post=boom)
    r = client.post("/sendWhatsApp", json={"to": "1", "message": "hi"})
    assert r.status_code == 502
