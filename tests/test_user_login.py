import pytest
from django.test import Client
from user_feedback.models import User


@pytest.mark.django_db
class TestUserLogin:

    PATH = "/api/user/login"
    INVALID_CREDENTIALS = "Invalid credentials"
    USERNAME_PASSWORD_REQUIRED = "Valid username and password are required"

    def setup_method(self, *args, **kwargs):
        """setup method for TestUserLogin"""
        self.client = Client()
        self.session_keys = ["user_id", "email", "last_name", "first_name"]
        self.test_user = User.objects.create(
            is_active=True,
            username="test",
            password="test",
            last_name="test",
            first_name="test",
            email="test@test.com",
        )

    def test_login(self, *args, **kwargs):
        """test to check login success"""
        payload = {
            "username": "test",
            "password": "test",
        }
        response = self.client.post(self.PATH, payload, content_type="application/json")
        assert response.status_code == 200
        data = response.json()
        session = data.get("session")
        assert isinstance(session, dict)
        assert session.get("user_id") == self.test_user.pk
        assert all(
            session.get(key) for key in self.session_keys
        ), "One or more keys are missing or have falsey values in the session."

    def test_login_without_username_password(self, *args, **kwargs):
        """test to check failed login due to invalid username and password"""
        response = self.client.post(
            self.PATH, payload={}, content_type="application/json"
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("message", "") == self.USERNAME_PASSWORD_REQUIRED

    def test_login_invalid_password(self, *args, **kwargs):
        """test to check invalid password"""
        payload = {"username": "test", "password": "invalid_password"}
        response = self.client.post(self.PATH, payload, content_type="application/json")
        assert response.status_code == 400
        data = response.json()
        assert data.get("message", "") == self.INVALID_CREDENTIALS

    def test_login_invalid_username(self, *args, **kwargs):
        """test to check invalid username"""
        payload = {"username": "invalid_username", "password": "password"}
        response = self.client.post(self.PATH, payload, content_type="application/json")
        assert response.status_code == 400
        data = response.json()
        assert data.get("message", "") == self.INVALID_CREDENTIALS
