import json


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = {} if payload is None else payload
        self.status_code = status_code
        self.text = json.dumps(self._payload)
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeRequests:
    """Stand-in for the `requests` module used inside app.py."""

    def __init__(self, get=None, post=None):
        self._get, self._post = get, post
        self.calls = []

    def get(self, url, **kw):
        self.calls.append(("GET", url, kw))
        return self._get(url, **kw)

    def post(self, url, **kw):
        self.calls.append(("POST", url, kw))
        return self._post(url, **kw)
