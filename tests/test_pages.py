from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User


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

    def test_inventory(self):
        response = self.client.get("/inventory")
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
