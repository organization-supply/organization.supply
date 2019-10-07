from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from dashboard.models import Location, Inventory, Product, Mutation


class TestDashboardPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )
        self.client.login(username="john", password="johnpassword")

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_dashboard(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)

    def test_inventory_location(self):
        response = self.client.get("/inventory/location")
        self.assertEqual(response.status_code, 200)

    def test_inventory_product(self):
        response = self.client.get("/inventory/product")
        self.assertEqual(response.status_code, 200)

    def test_products(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)

    def test_locations(self):
        response = self.client.get("/locations")
        self.assertEqual(response.status_code, 200)

    def test_mutations(self):
        response = self.client.get("/mutations")
        self.assertEqual(response.status_code, 200)

    def test_mutations_inser(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        response = self.client.post(
            "/mutations/insert",
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
