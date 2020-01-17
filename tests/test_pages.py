from base import TestBaseWithInventory
from django.test.client import Client

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestDashboardPages(TestBaseWithInventory):
    def setUp(self):
        super(TestDashboardPages, self).setUp()        

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_dashboard(self):
        response = self.client.get("/{}/dashboard".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_inventory_location(self):
        response = self.client.get(
            "/{}/inventory/location".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)

    def test_inventory_product(self):
        response = self.client.get(
            "/{}/inventory/product".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)

    def test_products(self):
        response = self.client.get("/{}/products".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_locations(self):
        response = self.client.get("/{}/locations".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_mutations(self):
        response = self.client.get("/{}/mutations".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_mutations_insert(self):
        response = self.client.post(
            "/{}/mutations/insert".format(self.organization.slug),
            {
                "amount": 1.0,
                "operation": "add",
                "location": self.location.id,
                "product": self.product.id,
                "desc": "Test transaction",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Transaction added!")

        self.assertEqual(Mutation.objects.count(), 1)

    def test_mutations_insert_with_missing_location(self):
        response = self.client.post(
            "/{}/mutations/insert".format(self.organization.slug),
            {
                "amount": 1.0,
                "operation": "add",
                "product": self.product.id,
                # Missing location: "location": self.location.id,
                "desc": "Test transaction",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Mutation.objects.count(), 0)
