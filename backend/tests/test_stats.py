import pytest


class TestStats:
    def test_get_stats(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_detections" in data
        assert "total_defects" in data
        assert "defect_rate" in data
        assert "class_distribution" in data

    def test_get_stats_without_auth(self, session, api_url):
        resp = session.get(f"{api_url}/stats")
        assert resp.status_code == 401 or resp.status_code == 403

    def test_get_stats_trend_default(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend")
        assert resp.status_code == 200
        data = resp.json()
        assert "trend" in data
        assert isinstance(data["trend"], list)

    def test_get_stats_trend_with_days(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend", params={"days": 30})
        assert resp.status_code == 200
        data = resp.json()
        assert "trend" in data

    def test_get_stats_trend_max_days(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend", params={"days": 90})
        assert resp.status_code == 200

    def test_get_stats_trend_invalid_days(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend", params={"days": 0})
        assert resp.status_code == 422

    def test_get_stats_trend_exceed_max(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend", params={"days": 100})
        assert resp.status_code == 422

    def test_get_defect_classes(self, session, api_url):
        resp = session.get(f"{api_url}/defect-classes")
        assert resp.status_code == 200
        data = resp.json()
        assert "classes" in data
        classes = data["classes"]
        assert isinstance(classes, dict)
        expected_keys = {0, 1, 2, 3, 4, 5}
        assert set(int(k) for k in classes.keys()) == expected_keys

    def test_stats_response_structure(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["total_detections"], int)
        assert isinstance(data["total_defects"], int)
        assert isinstance(data["defect_rate"], (int, float))
        assert isinstance(data["class_distribution"], dict)

    def test_trend_item_structure(self, auth_session, api_url):
        resp = auth_session.get(f"{api_url}/stats/trend", params={"days": 7})
        assert resp.status_code == 200
        data = resp.json()
        if data["trend"]:
            item = data["trend"][0]
            assert "date" in item
            assert "count" in item
