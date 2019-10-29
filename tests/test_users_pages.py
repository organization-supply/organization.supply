from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from dashboard.models import Location


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

    def test_settings(self):
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 200)

        # Test if the user is saved
        response = self.client.post(
            "/user/settings", {"first_name": "John", "last_name": "Lennon"}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Lennon")

        location = Location(name="Test Location")
        location.save()

        # Test if the profile is saved
        response = self.client.post(
            "/user/settings", {"location": location.id}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(user.profile.location, location)
