from django.test import TestCase
from django.test.client import Client

from organization.models import Inventory, Location, Mutation, Organization, Product
from user.models import User


class TestDashboardPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(name="test-org", url="http://test.com").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

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
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        product = Product(name="Test Product", organization=self.organization)
        product.save()

        response = self.client.post(
            "/{}/mutations/insert".format(self.organization.slug),
            {
                "amount": 1.0,
                "operation": "add",
                "location": location.id,
                "product": product.id,
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

        product = Product(name="Test Product", organization=self.organization)
        product.save()

        response = self.client.post(
            "/{}/mutations/insert".format(self.organization.slug),
            {
                "amount": 1.0,
                "operation": "add",
                "product": product.id,
                # Missing location
                "desc": "Test transaction",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Mutation.objects.count(), 0)
