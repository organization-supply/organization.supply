from django.test import TestCase
from django.test.client import Client
from rest_framework.test import APIClient

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestRestAPI(TestCase):
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
        self.client = APIClient(HTTP_AUTHORIZATION="Token: {}".format(self.token))
        # self.api_client =

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

    def test_api_product_view(self):
        # Create a product to test
        product = Product(name="Test Product", organization=self.organization)
        product.save()

        self._authenticate()

        # List
        response = self.client.get("/{}/api/products".format(self.organization.slug))
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Product")

        # Create
        response = self.client.post(
            "/{}/api/products".format(self.organization.slug),
            {"name": "API Product", "desc": "API Description"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "API Product")

        response = self.client.get("/{}/api/products".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_api_product_detail_view(self):
        # Create a product to test
        product = Product(name="Test Product", organization=self.organization)
        product.save()

        self._authenticate()

        # Get product
        response = self.client.get(
            "/{}/api/products/{}".format(self.organization.slug, product.id)
        )
        self.assertEqual(response.status_code, 200)

        # Patch product
        response = self.client.patch(
            "/{}/api/products/{}".format(self.organization.slug, product.id),
            {"name": "Patched API Product"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Patched API Product")
        self.assertEqual(response.json()["desc"], "")

        # Put product
        response = self.client.put(
            "/{}/api/products/{}".format(self.organization.slug, product.id),
            {"name": "Put API Product", "desc": "Put description"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Put API Product")
        self.assertEqual(response.json()["desc"], "Put description")

        # Delete product
        response = self.client.delete(
            "/{}/api/products/{}".format(self.organization.slug, product.id)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_api_location_view(self):
        # Create a location to test
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        self._authenticate()

        response = self.client.get("/{}/api/locations".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Location")

        # Create
        response = self.client.post(
            "/{}/api/locations".format(self.organization.slug),
            {"name": "API Location", "desc": "API Description"},
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get("/{}/api/locations".format(self.organization.slug))
        self.assertEqual(len(response.json()), 2)

    # def test_api_inventory(self):
    #     # Create a location to test
    #     location = Location(name="Test Location", organization=self.organization)
    #     location.save()
    #     # Create a product to test
    #     product = Product(name="Test Product", organization=self.organization)
    #     product.save()
    #     # Create an inventory to test
    #     inventory = Inventory(
    #         location=location, product=product, organization=self.organization
    #     )
    #     inventory.save()

    #     self._authenticate()

    #     response = self.client.get("/{}/api/inventory/".format(self.organization.slug))

    #     self.assertEqual(len(response.json()), 1)
    #     self.assertEqual(response.json()[0]["amount"], 0)
    #     self.assertEqual(response.json()[0]["product"], str(product.id))
    #     self.assertEqual(response.json()[0]["location"], str(location.id))

    #     response = self.client.get(
    #         "/{}/api/inventory/{}/".format(
    #             self.organization.slug, (response.json()[0]["id"])
    #         )
    #     )

    #     self.assertIn("location", response.json())
    #     self.assertIn("amount", response.json())
    #     self.assertEqual(response.json().get("location"), str(location.id))

    # def test_api_mutations(self):
    #     # TODO: fix this tests...
    #     # Create a location to test
    #     # location = Location(name="Test Location", organization=self.organization)
    #     # location.save()
    #     # # Create a product to test
    #     # product = Product(name="Test Product", organization=self.organization)
    #     # product.save()

    #     # # Create an inventory to test
    #     # inventory = Inventory(
    #     #     location=location, product=product, organization=self.organization
    #     # )
    #     # inventory.save()

    #     # mutation = Mutation(
    #     #     product=product,
    #     #     location=location,
    #     #     amount=10.0,
    #     #     organization=self.organization,
    #     # )
    #     # mutation.save()

    #     # self._authenticate()

    #     # response = self.client.get("/{}/api/mutations/".format(self.organization.slug))
    #     # self.assertEqual(len(response.json()), 1)
    #     # self.assertEqual(response.json()[0]["amount"], 10)
    #     # self.assertEqual(response.json()[0]["amount"], 9)
    #     pass
