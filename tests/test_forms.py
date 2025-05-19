import pytest
from django.test import Client
from user_feedback.models import User
from tests.constants import FORM_CREATION_PAYLOAD


@pytest.mark.django_db
class TestForms:
    GET_FORMS = "/api/forms/all"
    CREATE_FORM = "/api/form/new"
    GET_FORM = "/api/form/{form_id}"
    INVALID_PAYLOAD = "Invalid Payload"
    INVALID_SESSION = "Invalid Session"
    INVALID_FORM_ID = "Invalid form id"
    AUTHENTICATION_FAILED = "Authentication Error"
    GET_FORM_RESPONSES = "/api/form/{form_id}/responses"

    def set_session(self, data, *args, **kwargs):
        """set session values for test"""
        session = self.client.session
        session.update(data)
        session.save()

    def clear_session(self, *args, **kwargs):
        """clear current session"""
        session = self.client.session
        session.flush()

    def create_form(self, *args, **kwargs):
        """create form for unit test"""
        self.set_session({"user_id": self.test_user.pk})
        response = self.client.post(
            self.CREATE_FORM, FORM_CREATION_PAYLOAD, content_type="application/json"
        )
        form_data = response.json()
        form_id = form_data.get("form", {}).get("form_id")
        return form_id

    def setup_method(self, *args, **kwargs):
        """setup method for TestForms"""
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

    def test_fetch_all_forms_without_session(self, *args, **kwargs):
        """get forms without session"""
        response = self.client.get(self.GET_FORMS, content_type="application/json")
        assert response.status_code == 400
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("message") == self.INVALID_PAYLOAD

    def test_fetch_forms_with_session(self, *args, **kwargs):
        """get forms with session"""
        self.set_session({"user_id": self.test_user.pk})
        response = self.client.get(self.GET_FORMS, content_type="application/json")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        forms = data.get("forms")
        assert isinstance(forms, list)

    def test_create_form_without_session(self, *args, **kwargs):
        """create forms without session"""
        response = self.client.post(
            self.CREATE_FORM, FORM_CREATION_PAYLOAD, content_type="application/json"
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("message") == self.AUTHENTICATION_FAILED

    def test_create_form_with_session(self, *args, **kwargs):
        """create forms with session"""
        self.set_session({"user_id": self.test_user.pk})
        response = self.client.post(
            self.CREATE_FORM, FORM_CREATION_PAYLOAD, content_type="application/json"
        )
        assert response.status_code == 200
        data = response.json()
        form = data.get("form")
        form_id = form.get("form_id")
        form_title = form.get("form_title")
        created_at = form.get("created_at")
        assert all(
            [
                form,
                form_id,
                form_title,
                created_at,
                isinstance(form, dict),
                isinstance(form_id, int),
                isinstance(created_at, str),
                isinstance(form_title, str),
            ]
        )

    def test_get_form_using_form_id_without_session(self, *args, **kwargs):
        """get form using form id without session"""
        form_id = self.create_form()
        assert form_id
        self.clear_session()
        response = self.client.get(
            self.GET_FORM.format(form_id=form_id), content_type="application/json"
        )
        assert response.status_code == 400

    def test_get_form_using_form_id_with_session(self, *args, **kwargs):
        """get form with form and and session"""
        form_id = self.create_form()
        assert form_id
        response = self.client.get(
            self.GET_FORM.format(form_id=form_id), content_type="application/json"
        )
        assert response.status_code == 200
        data = response.json()
        id = data.get("form_id")
        title = data.get("form_title")
        fields = data.get("fields")
        assert all(
            [
                id,
                title,
                fields,
                len(fields),
                id == form_id,
                isinstance(title, str),
                isinstance(fields, list),
            ]
        )

    def test_download_form_responses_without_session(self, *args, **kwargs):
        """download form response without session"""
        form_id = self.create_form()
        assert form_id
        self.clear_session()
        response = self.client.get(
            self.GET_FORM_RESPONSES.format(form_id=form_id),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("message") == self.INVALID_SESSION

    def test_download_form_responses_with_session(self, *args, **kwargs):
        """download form responses with session"""
        form_id = self.create_form()
        assert form_id
        response = self.client.get(
            self.GET_FORM_RESPONSES.format(form_id=form_id),
            content_type="application/vnd.ms-excel",
        )
        assert response.status_code == 200
        assert (
            response["Content-Disposition"] == "attachment; filename=form-responses.xls"
        )
