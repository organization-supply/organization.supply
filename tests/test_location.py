from django.test import TestCase
from django.test.client import Client

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestLocationPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(name="test-org").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

    def test_locations(self):
        response = self.client.get("/{}/locations".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_create_location(self):
        response = self.client.get("/{}/location/new".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/{}/location/new".format(self.organization.slug),
            {"name": "Test Location", "desc": "Test Description"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()
        response = self.client.get(
            "/{}/location/{}".format(self.organization.slug, location.id)
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_location(self):
        response = self.client.post(
            "/{}/location/new".format(self.organization.slug),
            {"name": "Test Location", "desc": "Test Description"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()

        response = self.client.get(
            "/{}/location/{}/edit".format(self.organization.slug, location.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit: Test Location")

        response = self.client.post(
            "/{}/location/{}/edit".format(self.organization.slug, location.id),
            {"name": "Updated test Location", "desc": "Updated test Description"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Location.objects.count(), 1)

        location = Location.objects.get()

        self.assertEqual(location.name, "Updated test Location")
        self.assertEqual(location.desc, "Updated test Description")

    def test_delete_location(self):
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        self.assertEqual(Location.objects.count(), 1)

        response = self.client.post(
            "/{}/location/{}/edit".format(self.organization.slug, location.id),
            {"action": "delete"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Location deleted!")
        self.assertEqual(Location.objects.count(), 0)
