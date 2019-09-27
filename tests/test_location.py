from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from dashboard.models import Location


class TestLocationPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )
        self.client.login(username="john", password="johnpassword")

    def test_locations(self):
        response = self.client.get("/locations")
        self.assertEqual(response.status_code, 200)

    def test_create_location(self):
        response = self.client.post(
            "/location/new", {"name": "Test Location", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

    def test_edit_location(self):
        response = self.client.post(
            "/location/new", {"name": "Test Location", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()

        response = self.client.post(
            "/location/{}/edit".format(location.id),
            {"name": "Updated test Location", "desc": "Updated test Description"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()

        self.assertEqual(location.name, "Updated test Location")
        self.assertEqual(location.desc, "Updated test Description")

    def test_delete_location(self):
        pass
