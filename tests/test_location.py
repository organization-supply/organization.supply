from django.contrib.auth.models import User
from django.test import TestCase
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
        response = self.client.get("/location/new")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/location/new", {"name": "Test Location", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()
        response = self.client.get("/location/{}".format(location.id))
        self.assertEqual(response.status_code, 200)

    def test_edit_location(self):
        response = self.client.post(
            "/location/new", {"name": "Test Location", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()

        response = self.client.get("/location/{}/edit".format(location.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit: Test Location")

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
        location = Location(name="Test Location")
        location.save()

        self.assertEqual(Location.objects.count(), 1)

        response = self.client.post(
            "/location/{}/edit".format(location.id), {"action": "delete"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Location deleted!")
        self.assertEqual(Location.objects.count(), 0)
