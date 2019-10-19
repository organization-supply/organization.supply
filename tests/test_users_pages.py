from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class TestUserPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )
        self.client.login(username="john", password="johnpassword")

    def test_login(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        pass
