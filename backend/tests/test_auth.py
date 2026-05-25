import uuid

import pytest


class TestRegister:
    def test_register_success(self, session, api_url):
        username = f"reg_test_{uuid.uuid4().hex[:8]}"
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": "test123456"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["token"] != ""
        assert data["username"] == username

    def test_register_duplicate_username(self, session, api_url):
        username = f"dup_test_{uuid.uuid4().hex[:8]}"
        session.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": "test123456"},
        )
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": "test123456"},
        )
        assert resp.status_code == 400

    def test_register_empty_username(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": "", "password": "test123456"},
        )
        assert resp.status_code == 400

    def test_register_empty_password(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": "someuser", "password": ""},
        )
        assert resp.status_code == 400

    def test_register_short_username(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": "ab", "password": "test123456"},
        )
        assert resp.status_code == 400

    def test_register_short_password(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/register",
            json={"username": "validuser", "password": "12345"},
        )
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, session, api_url):
        username = f"login_test_{uuid.uuid4().hex[:8]}"
        password = "test123456"
        session.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": password},
        )
        resp = session.post(
            f"{api_url}/auth/login",
            json={"username": username, "password": password},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["token"] != ""
        assert data["username"] == username

    def test_login_wrong_password(self, session, api_url):
        username = f"loginwp_{uuid.uuid4().hex[:8]}"
        session.post(
            f"{api_url}/auth/register",
            json={"username": username, "password": "test123456"},
        )
        resp = session.post(
            f"{api_url}/auth/login",
            json={"username": username, "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/login",
            json={"username": "nonexistent_user_xyz", "password": "test123456"},
        )
        assert resp.status_code == 401

    def test_login_empty_credentials(self, session, api_url):
        resp = session.post(
            f"{api_url}/auth/login",
            json={"username": "", "password": ""},
        )
        assert resp.status_code == 400


class TestGetCurrentUser:
    def test_get_me_with_valid_token(self, session, api_url, auth_token):
        resp = session.get(
            f"{api_url}/auth/me",
            params={"token": auth_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data

    def test_get_me_without_token(self, session, api_url):
        resp = session.get(f"{api_url}/auth/me")
        assert resp.status_code == 401

    def test_get_me_with_invalid_token(self, session, api_url):
        resp = session.get(
            f"{api_url}/auth/me",
            params={"token": "invalid_token_xyz"},
        )
        assert resp.status_code == 401
