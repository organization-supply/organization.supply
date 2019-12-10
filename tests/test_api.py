from django.test import TestCase
from django.test.client import Client

from organization.models import Inventory, Location, Mutation, Organization, Product
from user.models import User


class TestUserPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")

        Organization(name="test-org").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

    def _authenticate(self):
        response = self.client.post(
            "/{}/api/auth".format(self.organization.slug),
            {"username": "lennon@thebeatles.com", "password": "johnpassword"},
            follow=True,
        )

        self.token = response.json().get("token")
        self.client = Client(HTTP_AUTHORIZATION="Token: {}".format(self.token))

    def test_api_auth(self):
        response = self.client.post(
            "/{}/api/auth".format(self.organization.slug),
            {"username": "lennon@thebeatles.com", "password": "johnpassword"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())
        self.assertIn("user", response.json())
        self.assertIn("organization", response.json())
        self.assertEqual(response.json().get("organization"), self.organization.slug)
        self.assertEqual(response.json().get("user"), self.user.username)

    def test_api_products(self):
        # Create a product to test
        product = Product(name="Test Product", organization=self.organization)
        product.save()

        self._authenticate()

        response = self.client.get("/{}/api/products/".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Product")

        response = self.client.get(
            "/{}/api/products/{}/".format(
                self.organization.slug, (response.json()[0]["id"])
            )
        )

        self.assertIn("name", response.json())
        self.assertEqual(response.json().get("name"), "Test Product")

    def test_api_location(self):
        # Create a location to test
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        self._authenticate()

        response = self.client.get("/{}/api/locations/".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Location")

        response = self.client.get(
            "/{}/api/locations/{}/".format(
                self.organization.slug, (response.json()[0]["id"])
            )
        )

        self.assertIn("name", response.json())
        self.assertEqual(response.json().get("name"), "Test Location")

    def test_api_inventory(self):
        # Create a location to test
        location = Location(name="Test Location", organization=self.organization)
        location.save()
        # Create a product to test
        product = Product(name="Test Product", organization=self.organization)
        product.save()
        # Create an inventory to test
        inventory = Inventory(
            location=location, product=product, organization=self.organization
        )
        inventory.save()

        self._authenticate()

        response = self.client.get("/{}/api/inventory/".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["amount"], 0)
        self.assertEqual(response.json()[0]["product"], str(product.id))
        self.assertEqual(response.json()[0]["location"], str(location.id))

        response = self.client.get(
            "/{}/api/inventory/{}/".format(
                self.organization.slug, (response.json()[0]["id"])
            )
        )

        self.assertIn("location", response.json())
        self.assertIn("amount", response.json())
        self.assertEqual(response.json().get("location"), str(location.id))

    def test_api_mutations(self):
        # TODO: fix this tests...
        # Create a location to test
        # location = Location(name="Test Location", organization=self.organization)
        # location.save()
        # # Create a product to test
        # product = Product(name="Test Product", organization=self.organization)
        # product.save()

        # # Create an inventory to test
        # inventory = Inventory(
        #     location=location, product=product, organization=self.organization
        # )
        # inventory.save()

        # mutation = Mutation(
        #     product=product,
        #     location=location,
        #     amount=10.0,
        #     organization=self.organization,
        # )
        # mutation.save()

        # self._authenticate()
        
        # response = self.client.get("/{}/api/mutations/".format(self.organization.slug))
        # self.assertEqual(len(response.json()), 1)
        # self.assertEqual(response.json()[0]["amount"], 10)
        # self.assertEqual(response.json()[0]["amount"], 9)
        pass