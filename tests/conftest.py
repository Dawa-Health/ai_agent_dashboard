import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app as app_module  # noqa: E402
from fakes import FakeRequests  # noqa: E402


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise requests.ConnectionError("network disabled in tests")
    monkeypatch.setattr(requests.sessions.Session, "request", blocked)


@pytest.fixture(autouse=True)
def clean_cache():
    app_module.QR_CACHE.update(payload=None, expires_at=0)
    yield
    app_module.QR_CACHE.update(payload=None, expires_at=0)


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


@pytest.fixture
def install_requests(monkeypatch):
    def _install(get=None, post=None):
        fake = FakeRequests(get, post)
        monkeypatch.setattr(app_module, "requests", fake)
        return fake
    return _install
