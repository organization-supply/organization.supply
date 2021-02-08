import re

from django.core import mail
from django.test.client import Client
from organizations.backends.tokens import RegistrationTokenGenerator

from base import TestBase
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestOrganizationInvite(TestBase):
    def setUp(self):
        super(TestOrganizationInvite, self).setUp()

    def test_create_invite_existing_user(self):
        self.user_2 = User.objects.create_user(
            "mccartney@thebeatles.com", "paulpassword"
        )

        response = self.client.get("/{}/users".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/{}/users/invite".format(self.organization.slug),
            {"email": "mccartney@thebeatles.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "mccartney@thebeatles.com invited for Test Organization",
            response.content.decode(),
        )

        self.assertIn(self.user_2, self.organization.users.all())

    def test_create_invite_new_user(self):
        # Create invite
        response = self.client.post(
            "/{}/users/invite".format(self.organization.slug),
            {"email": "mccartney@thebeatles.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "mccartney@thebeatles.com invited for Test Organization",
            response.content.decode(),
        )

        # There should be one email for the invite.
        self.assertEqual(len(mail.outbox), 1)

        self.assertIn(
            "You've been invited to join Test Organization", mail.outbox[0].subject
        )

        # There should be an inactive user created
        invited_user = User.objects.get(email="mccartney@thebeatles.com")
        self.assertEqual(invited_user.is_active, False)

        # Regex to find the URL in the body of the email
        link = re.compile(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        register_url = link.search(mail.outbox[0].body)[0]

        # Log the current user out for now
        self.client.logout()

        # The register url should give a 200.
        response = self.client.get(register_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            register_url,
            {
                "email": "mccartney@thebeatles.com",
                "password": "paulpassword",
                "password_confirm": "invalidsecondpassword",
            },
            follow=True,
        )

        self.assertIn("Your password entries must match", response.content.decode())

        response = self.client.post(
            register_url,
            {
                "email": "mccartney@thebeatles.com",
                "password": "paulpassword",
                "password_confirm": "paulpassword",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            User.objects.get(email="mccartney@thebeatles.com"),
            self.organization.users.all(),
        )

        # The register url should give a 404, since it's expired
        response = self.client.get(register_url)
        self.assertIn("Page not found", response.content.decode())

        # The incorrect register url should give a 404, since its invalid
        response = self.client.get(register_url[:-1] + "1")
        self.assertIn("Page not found", response.content.decode())

    def test_organization_remove_user(self):
        self.user_2 = User.objects.create_user(
            "mccartney@thebeatles.com", "paulpassword"
        )
        self.organization.add_user(self.user_2)
        self.assertEqual(self.organization.users.count(), 2)

        response = self.client.get(
            "/{}/users/remove?id={}".format(self.organization.slug, self.user_2.pk),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.organization.users.count(), 1)

        # Try and see if we remove ourselves
        response = self.client.get(
            "/{}/users/remove?id={}".format(self.organization.slug, self.user.pk),
            follow=True,
        )
        self.assertIn(
            "You cannot remove yourself from this organization",
            response.content.decode(),
        )
