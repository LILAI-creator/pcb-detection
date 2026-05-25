import pytest


class TestModelList:
    def test_list_models(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/models/list")
        assert resp.status_code == 200

    def test_list_models_without_auth(self, session, api_url):
        resp = session.get(f"{api_url}/models/list")
        assert resp.status_code == 401 or resp.status_code == 403


class TestModelUpload:
    def test_upload_non_pt_file(self, auth_session, api_url):
        resp = auth_session.post(
            f"{api_url}/models/upload",
            files={"file": ("model.txt", b"not a model", "text/plain")},
        )
        assert resp.status_code == 400

    def test_upload_without_auth(self, session, api_url):
        resp = session.post(
            f"{api_url}/models/upload",
            files={"file": ("model.pt", b"fake", "application/octet-stream")},
        )
        assert resp.status_code == 401 or resp.status_code == 403

    def test_upload_empty_file(self, auth_session, api_url):
        resp = auth_session.post(
            f"{api_url}/models/upload",
            files={"file": ("model.pt", b"", "application/octet-stream")},
        )
        assert resp.status_code in (400, 500)


class TestModelSwitch:
    def test_switch_nonexistent_model(self, auth_session, api_url):
        resp = auth_session.post(
            f"{api_url}/models/switch", params={"model_id": 99999}
        )
        assert resp.status_code == 400

    def test_switch_without_auth(self, session, api_url):
        resp = session.post(
            f"{api_url}/models/switch", params={"model_id": 1}
        )
        assert resp.status_code == 401 or resp.status_code == 403


class TestModelDelete:
    def test_delete_nonexistent_model(self, auth_session, api_url):
        resp = auth_session.delete(f"{api_url}/models/99999")
        assert resp.status_code == 400

    def test_delete_without_auth(self, session, api_url):
        resp = session.delete(f"{api_url}/models/1")
        assert resp.status_code == 401 or resp.status_code == 403


class TestModelWorkflow:
    def test_list_models_response_structure(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/models/list")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))
