from rest_framework.test import APIClient

from base import TestBaseWithInventory
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestRestAPI(TestBaseWithInventory):
    def setUp(self):
        super(TestRestAPI, self).setUp()

    def _authenticate(self):
        response = self.client.post(
            "/{}/api/auth".format(self.organization.slug),
            {"username": "lennon@thebeatles.com", "password": "johnpassword"},
            follow=True,
        )

        self.token = response.json().get("token")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

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

    def test_api_user_view(self):
        self._authenticate()

        response = self.client.get("/{}/api/me".format(self.organization.slug))
        self.assertIn("id", response.json())
        self.assertIn("email", response.json())
        self.assertIn("name", response.json())

        self.assertEqual(response.json().get("id"), str(self.user.id))
        self.assertEqual(response.json().get("email"), self.user.email)

    def test_api_product_view(self):
        self._authenticate()

        # List
        response = self.client.get("/{}/api/products".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Product")
        self.assertIn("image", response.json()[0])

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
        self.assertEqual(response.json()[1]["name"], "API Product")

    def test_api_product_detail_view(self):
        self._authenticate()

        # Get product
        response = self.client.get(
            "/{}/api/products/{}".format(self.organization.slug, self.product.id)
        )
        self.assertEqual(response.status_code, 200)

        # Patch product
        response = self.client.patch(
            "/{}/api/products/{}".format(self.organization.slug, self.product.id),
            {"name": "Patched API Product"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Patched API Product")
        self.assertEqual(response.json()["desc"], "")
        self.assertEqual(
            response.json()["image"],
            "http://testserver/media/organization/product/default.png",
        )

        # Put product
        response = self.client.put(
            "/{}/api/products/{}".format(self.organization.slug, self.product.id),
            {"name": "Put API Product", "desc": "Put description"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Put API Product")
        self.assertEqual(response.json()["desc"], "Put description")
        self.assertEqual(
            response.json()["image"],
            "http://testserver/media/organization/product/default.png",
        )

        # Set the inventory to 0 and then delete the product
        self.inventory.amount = 0
        self.inventory.save()

        response = self.client.delete(
            "/{}/api/products/{}".format(self.organization.slug, self.product.id)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_api_location_view(self):
        self._authenticate()

        response = self.client.get("/{}/api/locations".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Location")
        self.assertIn("image", response.json()[0])

        # Create
        response = self.client.post(
            "/{}/api/locations".format(self.organization.slug),
            {"name": "API Location", "desc": "API Description"},
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get("/{}/api/locations".format(self.organization.slug))
        self.assertEqual(len(response.json()), 2)

    def test_api_location_detail_view(self):
        self._authenticate()

        # Get location
        response = self.client.get(
            "/{}/api/locations/{}".format(self.organization.slug, self.location.id)
        )
        self.assertEqual(response.status_code, 200)

        # Patch location
        response = self.client.patch(
            "/{}/api/locations/{}".format(self.organization.slug, self.location.id),
            {"name": "Patched API Location"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Patched API Location")
        self.assertEqual(response.json()["desc"], "")
        self.assertEqual(
            response.json()["image"],
            "http://testserver/media/organization/location/default.png",
        )
        self.assertEqual(response.json()["tags"], [])

        # Put location
        response = self.client.put(
            "/{}/api/locations/{}".format(self.organization.slug, self.location.id),
            {"name": "Put API Location", "desc": "Put description"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Put API Location")
        self.assertEqual(response.json()["desc"], "Put description")
        self.assertEqual(
            response.json()["image"],
            "http://testserver/media/organization/location/default.png",
        )
        self.assertEqual(response.json()["tags"], [])

        # Set the inventory to 0 and then delete the location
        self.inventory.amount = 0
        self.inventory.save()

        response = self.client.delete(
            "/{}/api/locations/{}".format(self.organization.slug, self.location.id)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Location.objects.count(), 0)

    def test_api_inventory(self):

        self._authenticate()

        response = self.client.get("/{}/api/inventory".format(self.organization.slug))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["amount"], 100)
        self.assertEqual(response.json()[0]["product"], str(self.product.id))
        self.assertEqual(response.json()[0]["location"], str(self.location.id))

    def test_api_mutations(self):

        # Create a mutation
        mutation = Mutation(
            product=self.product,
            location=self.location,
            amount=10.0,
            organization=self.organization,
        )
        mutation.save()

        self._authenticate()

        response = self.client.get("/{}/api/mutations".format(self.organization.slug))
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["amount"], 10)

    def test_api_notifications(self):
        self._authenticate()

        response = self.client.get(
            "/{}/api/notifications".format(self.organization.slug)
        )
        self.assertEqual(len(response.json()), 0)  # there should be no notifications
