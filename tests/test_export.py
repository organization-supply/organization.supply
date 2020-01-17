import io

from base import TestBaseWithInventory
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestOrganizationExport(TestBaseWithInventory):
    def setUp(self):
        super(TestOrganizationExport, self).setUp()

    def test_export_page(self):
        response = self.client.get("/{}/export".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_export_entity_not_found(self):
        response = self.client.get(
            "/{}/export/non-existing-entity".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 404)

    def test_export_product(self):
        response = self.client.get("/{}/export/products".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "csv")
        self.assertIn(b"Test Product", b"".join(response.streaming_content))

    def test_export_locations(self):
        response = self.client.get(
            "/{}/export/locations".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "csv")
        self.assertIn(b"Test Location", b"".join(response.streaming_content))

    def test_export_inventory(self):
        response = self.client.get(
            "/{}/export/inventory".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "csv")
        self.assertIn(b"100", b"".join(response.streaming_content))

    def test_export_mutations(self):
        pass

    def test_export_users(self):
        pass
