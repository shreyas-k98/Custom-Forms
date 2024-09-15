import pytest
from django.test import Client


@pytest.mark.django_db
class TestUserLogout:

    PATH = "/api/user/logout"
    LOGOUT_SUCCESS = "User logged out successfully"

    def setup_method(self, *args, **kwargs):
        """setup method for TestUserLogout"""
        self.client = Client()

    def test_logout_without_session(self, *args, **kwargs):
        """Test logout when no user is logged in (no session)."""
        response = self.client.get(self.PATH)
        assert response.status_code == 200
        assert response.json() == {}

    def test_logout_with_session(self, *args, **kwargs):
        """Test logout when a user session exists."""
        session = self.client.session
        session.update({"user_id": 1})
        session.save()
        response = self.client.get(self.PATH)
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == self.LOGOUT_SUCCESS
        assert "user_id" not in self.client.session
