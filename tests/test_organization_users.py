import re

from django.core import mail
from django.test import TestCase
from django.test.client import Client
from organizations.backends.tokens import RegistrationTokenGenerator

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestOrganizationUsers(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.user_2 = User.objects.create_user("mccartney@thebeatles.com", "paulpassword")
        Organization(name="Test Organization").save()
        self.organization = Organization.objects.get(name="Test Organization")
        self.organization.add_user(self.user)
        self.organization.add_user(self.user_2)

        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")

    def test_organization_leave(self):
        response = self.client.get("/user/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Organization", response.content.decode())
        self.assertIn("Leave", response.content.decode())

        response = self.client.get("/{}/users/leave".format(self.organization.slug), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("You left {}".format(self.organization.name), response.content.decode())

    def test_organization_leave_admin(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get("/user/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Organization", response.content.decode())
        self.assertIn("Leave", response.content.decode())

        response = self.client.get("/{}/users/leave".format(self.organization.slug), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("You cannot leave {}  because you are an admin".format(self.organization.name), response.content.decode())

        