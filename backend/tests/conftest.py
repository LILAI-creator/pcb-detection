import uuid

import pytest
import requests

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api_url(base_url):
    return f"{base_url}{API_PREFIX}"


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def test_username():
    return f"pytest_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def test_password():
    return "pytest123456"


@pytest.fixture(scope="session")
def registered_user(session, api_url, test_username, test_password):
    resp = session.post(
        f"{api_url}/auth/register",
        json={"username": test_username, "password": test_password},
    )
    if resp.status_code == 200 and resp.json().get("token"):
        token = resp.json()["token"]
    else:
        login_resp = session.post(
            f"{api_url}/auth/login",
            json={"username": test_username, "password": test_password},
        )
        token = login_resp.json()["token"]
    yield {
        "username": test_username,
        "password": test_password,
        "token": token,
    }


@pytest.fixture(scope="session")
def auth_token(registered_user):
    return registered_user["token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def auth_session(auth_headers):
    s = requests.Session()
    s.headers.update(auth_headers)
    return s


@pytest.fixture(scope="session")
def logged_in_user(session, api_url, test_username, test_password):
    resp = session.post(
        f"{api_url}/auth/login",
        json={"username": test_username, "password": test_password},
    )
    return resp.json()


def pytest_collection_modifyitems(items):
    for item in items:
        if "auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
        elif "detect" in item.nodeid:
            item.add_marker(pytest.mark.detect)
        elif "history" in item.nodeid:
            item.add_marker(pytest.mark.history)
        elif "stats" in item.nodeid:
            item.add_marker(pytest.mark.stats)
        elif "model" in item.nodeid:
            item.add_marker(pytest.mark.model)
