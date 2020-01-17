import re

from django.core import mail
from django.test.client import Client
from organizations.backends.tokens import RegistrationTokenGenerator

from base import TestBase
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestOrganizationUsers(TestBase):
    def setUp(self):
        super(TestOrganizationUsers, self).setUp()
        self.user_2 = User.objects.create_user(
            "mccartney@thebeatles.com", "paulpassword"
        )
        self.organization.add_user(self.user_2)

    def test_organization_leave(self):
        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")

        response = self.client.get("/user/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Organization", response.content.decode())
        self.assertIn("Leave", response.content.decode())

        response = self.client.get(
            "/{}/users/leave".format(self.organization.slug), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You left {}".format(self.organization.name), response.content.decode()
        )

    def test_organization_leave_admin(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get("/user/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Organization", response.content.decode())
        self.assertIn("Leave", response.content.decode())

        response = self.client.get(
            "/{}/users/leave".format(self.organization.slug), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "You cannot leave {}  because you are an admin".format(
                self.organization.name
            ),
            response.content.decode(),
        )
