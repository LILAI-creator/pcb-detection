import pytest


class TestHistory:
    def test_get_history_default(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_history_with_pagination(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/history", params={"page": 1, "page_size": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 5

    def test_get_history_with_page_size_limit(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/history", params={"page_size": 100})
        assert resp.status_code == 200

    def test_get_history_with_defect_class_filter(self, auth_session, api_url):
        resp = auth_session.get(
            f"{api_url}/history", params={"defect_class": "missing_hole"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    def test_get_history_with_date_filter(self, auth_session, api_url):
        resp = auth_session.get(
            f"{api_url}/history",
            params={"start_date": "2020-01-01", "end_date": "2030-12-31"},
        )
        assert resp.status_code == 200

    def test_get_history_without_auth(self, session, api_url):
        resp = session.get(f"{api_url}/history")
        assert resp.status_code == 401 or resp.status_code == 403

    def test_get_history_detail_valid_id(self, auth_session, api_url):
        history_resp = auth_session.get(f"{api_url}/history", params={"page_size": 1})
        assert history_resp.status_code == 200
        data = history_resp.json()
        if data["total"] == 0:
            pytest.skip("暂无历史记录")
        record_id = data["items"][0]["id"]
        resp = auth_session.get(f"{api_url}/history/{record_id}")
        assert resp.status_code == 200

    def test_get_history_detail_invalid_id(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/history/nonexistent_id_99999")
        assert resp.status_code == 404

    def test_history_response_structure(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/history")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)
        if data["total"] > 0:
            item = data["items"][0]
            assert "id" in item
            assert "timestamp" in item
            assert "defects" in item
