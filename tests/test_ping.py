import pytest
from django.test import Client


class TestPing:

    PATH = "/api/ping"

    def setup_method(self, *args, **kwargs):
        """setup method for TestPing"""
        self.client = Client()

    def test_ping(self, *args, **kwargs):
        response = self.client.get(self.PATH)
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "pong"
