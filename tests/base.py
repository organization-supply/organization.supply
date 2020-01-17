from django.test import TestCase
from django.test.client import Client

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestBase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(
            name="Test Organization", contact_email="org@thebeatles.com"
        ).save()
        self.organization = Organization.objects.get(name="Test Organization")
        self.organization.add_user(self.user)


class TestBaseWithInventory(TestBase):
    def setUp(self):
        super(TestBaseWithInventory, self).setUp()

        self.product = Product(name="Test Product", organization=self.organization)
        self.product.save()

        self.location = Location(name="Test Location", organization=self.organization)
        self.location.save()

        self.inventory = Inventory(
            organization=self.organization,
            product=self.product,
            location=self.location,
            amount=100,
        )
        self.inventory.save()
