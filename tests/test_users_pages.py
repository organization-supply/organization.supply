from django.test import TestCase
from django.test.client import Client

from organization.models.organization import Organization
from user.models import User


class TestUserPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(name="test-org").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

    def test_signup(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/user/signup",
            {"email": "mccartney@thebeatles.com", "password": "paulpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Signup succesfull!", response.content.decode())

        response = self.client.post(
            "/user/signup",
            {"email": "mccartney@thebeatles.com", "password": "paulpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "User with this Email address already exists", response.content.decode()
        )

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
