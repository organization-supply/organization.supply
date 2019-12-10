from django.test import TestCase
from django.test.client import Client

from organization.models import Inventory, Location, Mutation, Organization, Product
from user.models import User


class TestSearch(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(name="test-org").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

    def test_search(self):
        response = self.client.get("/{}/search".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_search_result(self):
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        product = Product(name="Test Product", organization=self.organization)
        product.save()

        response = self.client.get("/{}/search?q=Test".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Location", response.content.decode())
        self.assertIn("Test Product", response.content.decode())
        self.assertNotIn("lennon@thebeatles.com", response.content.decode())

        # Test case insensitity
        response = self.client.get("/{}/search?q=test".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

        self.assertIn("Test Location", response.content.decode())
        self.assertIn("Test Product", response.content.decode())
        self.assertNotIn("lennon@thebeatles.com", response.content.decode())

        # Test finding a user
        response = self.client.get("/{}/search?q=lennon".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Test Location", response.content.decode())
        self.assertNotIn("Test Product", response.content.decode())
        self.assertIn("lennon@thebeatles.com", response.content.decode())
