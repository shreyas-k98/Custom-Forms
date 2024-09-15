import pytest
from django.test import Client
from user_feedback.models import User
from tests.constants import USER_SIGNUP_PAYLOAD


@pytest.mark.django_db
class TestUserSignup:

    PATH = "/api/user/new"
    INVALID_PAYLOAD = "Invalid payload"
    SIGNUP_SUCCESS = "User saved successfully"
    USERNAME_EXISTS = "Username already exists"

    def setup_method(self, *args, **kwargs):
        """setup method for TestUserSignup"""
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

    def test_user_signup(self, *aegs, **kwargs):
        response = self.client.post(
            self.PATH, USER_SIGNUP_PAYLOAD, content_type="application/json"
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == self.SIGNUP_SUCCESS

    def test_user_signup_username_exists(self, *args, **kwargs):
        payload = dict(**USER_SIGNUP_PAYLOAD)
        payload.update({"username": "test"})
        response = self.client.post(self.PATH, payload, content_type="application/json")
        assert response.status_code == 400
        data = response.json()
        assert data.get("message") == self.USERNAME_EXISTS

    def test_user_signup_invalid_payload(self, *args, **kwargs):
        response = self.client.post(self.PATH, {}, content_type="application/json")
        assert response.status_code == 400
        data = response.json()
        assert data.get("message") == self.INVALID_PAYLOAD
