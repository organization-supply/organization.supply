from django.test import TestCase
from django.test.client import Client
from organizations.utils import create_organization

from user.models import User


class TestUserPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        self.organization = create_organization(
            self.user, "test-org", org_user_defaults={"is_admin": True}
        )

    def test_signup(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get("/user/login/")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get("/user/logout/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 200)

        # Test if the user is saved
        response = self.client.post(
            "/user/settings", {"name": "John Lennon"}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.name, "John Lennon")
