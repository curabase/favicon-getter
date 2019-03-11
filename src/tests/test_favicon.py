import app
from favicon_extractor import FavIconException
import pytest

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    yield client


def test_empty_url_param(client):

    r = client.get('/')
    assert r.status_code == 400
    assert r.data == b'url cannot be None'


def test_no_domain_in_url(client):
    r = client.get('/?url=http://')
    assert r.status_code == 400
    assert r.data == b'Missing domain'


def test_ssh_scheme(client):
    r = client.get('/?url=ssh://user@host')
    assert r.status_code == 200


def test_localhost_scheme(client):
    r = client.get('/?url=http://localhost:8080')
    assert r.status_code == 200


def test_already_cached_favicon(client):
    r = client.get('/?url=http://google.com')
    assert r.status_code == 200

