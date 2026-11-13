import pytest
import app as app_module

rules = [r for r in app_module.app.url_map.iter_rules() if r.endpoint != "static"]
get_paths = sorted(r.rule for r in rules if "GET" in r.methods and not r.arguments)
post_paths = sorted(r.rule for r in rules if "POST" in r.methods and not r.arguments)


@pytest.mark.parametrize("path", get_paths)
def test_get_route_does_not_crash(client, path):
    assert client.get(path).status_code < 500


@pytest.mark.parametrize("path", post_paths)
def test_post_with_empty_body_is_rejected_cleanly(client, path):
    assert client.post(path, json={}).status_code < 500
