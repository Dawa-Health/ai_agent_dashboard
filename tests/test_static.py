import pytest


def test_root_serves_chats_page(client):
    assert client.get("/").status_code == 200


@pytest.mark.parametrize("page", ["login.html", "register.html", "analytics.html"])
def test_html_pages_are_served(client, page):
    assert client.get(f"/{page}").status_code == 200


@pytest.mark.parametrize("path", ["/app.py", "/requirements.txt", "/.gitignore", "/LICENSE"])
def test_source_and_config_files_are_not_served(client, path):
    assert client.get(path).status_code == 404


def test_missing_asset_is_404(client):
    assert client.get("/css/does-not-exist.css").status_code == 404


from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("folder", ["css", "js", "img"])
def test_asset_routes_serve_a_real_file(client, folder):
    first = next(p for p in sorted((ROOT / folder).iterdir()) if p.is_file())
    resp = client.get(f"/{folder}/{first.name}")
    assert resp.status_code == 200
    resp.close()


@pytest.mark.parametrize("folder", ["css", "js", "img"])
def test_asset_routes_block_path_traversal(client, folder):
    assert client.get(f"/{folder}/../app.py").status_code == 404
    assert client.get(f"/{folder}/%2e%2e/app.py").status_code == 404
