import pytest
from django.test import Client


@pytest.mark.django_db
class TestSession:

    PATH = "/api/data/session"

    def setup_method(self, *args, **kwargs):
        """setup method for TestUserLogout"""
        self.client = Client()

    def test_session_response(self, *args, **kwargs):
        """test session api for empty session"""
        response = self.client.get(self.PATH)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data == {}

    def test_session_data(self, *args, **kwargs):
        """test session api response for non-empty session"""
        session = self.client.session
        session.update({"user_id": 1})
        session.save()
        response = self.client.get(self.PATH)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("user_id") == 1
