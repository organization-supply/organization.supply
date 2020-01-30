from django.test.client import Client

from base import TestBaseWithStaffUser
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestDeckPages(TestBaseWithStaffUser):
    def setUp(self):
        super(TestDeckPages, self).setUp()

    # The deck should be reachable by a staff user
    def test_deck_non_staff_user(self):
        response = self.client.get("/deck/", follow=True)
        self.assertEqual(response.status_code, 404)

    # But not by a normal user:
    def test_deck_staff_user(self):
        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")
        response = self.client.get("/deck/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Organization", response.content.decode())
