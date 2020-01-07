from django.test import TestCase
from django.test.client import Client

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.organization import Organization
from user.models import User


class TestOrganizationCreate(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")

    def test_create_organization(self):
        response = self.client.get("/create")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/create", {"name": "Test Organization"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Organization.objects.count())
        self.assertEqual("Test Organization", Organization.objects.get().name)
        self.assertEqual("test-organization", Organization.objects.get().slug)

    def test_create_organization_invalid_name(self):
        response = self.client.post("/create", {"name": "Admin"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Name is not available", response.content.decode())

        response = self.client.post("/create", {"name": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required", response.content.decode())


class TestOrganizationSettings(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        Organization(name="Test Organization").save()
        self.organization = Organization.objects.get(name="Test Organization")
        self.organization.add_user(self.user)

    def test_organization_settings(self):
        response = self.client.get("/{}/settings".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/{}/settings".format(self.organization.slug),
            {"name": "New Organization Name"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Organization.objects.get(name="New Organization Name"))
        # TODO: fix so we update the slug too..., this currently doesn't work..

    def test_organization_users(self):
        response = self.client.get("/{}/users".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)

    def test_organization_integrations(self):
        response = self.client.get("/{}/integrations".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)


class TestOrganizationPermissions(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("lennon@thebeatles.com", "johnpassword")
        self.user_2 = User.objects.create_user(
            "mccartney@thebeatles.com", "paulpassword"
        )

        Organization(name="test-org").save()
        self.organization = Organization.objects.get(name="test-org")
        self.organization.add_user(self.user)

        Organization(name="test-org-2").save()
        self.organization_2 = Organization.objects.get(name="test-org-2")
        self.organization_2.add_user(self.user_2)

        self.client.login(email="lennon@thebeatles.com", password="johnpassword")

    def test_products_should_only_be_seen_by_the_organization(self):
        # Create a product for the first organization
        product = Product(name="Test Product", organization=self.organization)
        product.save()

        # The product should be available for the first organization with the first user logged in
        response = self.client.get(
            "/{}/product/{}".format(self.organization.slug, product.id)
        )
        self.assertEqual(response.status_code, 200)

        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")

        # The second user with a different organization should not be able to see it
        response = self.client.get(
            "/{}/product/{}".format(self.organization_2.slug, product.id)
        )
        self.assertEqual(response.status_code, 404)

        # Even when forcing the url to be the same as organization 1
        response = self.client.get(
            "/{}/product/{}".format(self.organization.slug, product.id)
        )
        self.assertEqual(response.status_code, 404)

    def test_location_should_only_be_seen_by_the_organization(self):
        # Create a location for the first organization
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        # The location should be available for the first organization with the first user logged in
        response = self.client.get(
            "/{}/location/{}".format(self.organization.slug, location.id)
        )
        self.assertEqual(response.status_code, 200)

        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")

        # The second user with a different organization should not be able to see it
        response = self.client.get(
            "/{}/location/{}".format(self.organization_2.slug, location.id)
        )
        self.assertEqual(response.status_code, 404)

        # Even when forcing the url to be the same as organization 1
        response = self.client.get(
            "/{}/location/{}".format(self.organization.slug, location.id)
        )
        self.assertEqual(response.status_code, 404)

    def test_inventory_should_only_be_seen_by_the_organization(self):
        # Create a location for the first organization
        location = Location(name="Test Location", organization=self.organization)
        location.save()

        # Create a location for the first organization
        product = Product(name="Test Product", organization=self.organization)
        product.save()

        inventory = Inventory(
            location=location,
            product=product,
            organization=self.organization,
            amount=10,
        )
        inventory.save()

        # The inventory should be available for the first organization with the first user logged in
        response = self.client.get(
            "/{}/inventory/location".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Location", response.content.decode())

        response = self.client.get(
            "/{}/inventory/product".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Product", response.content.decode())

        self.client.login(email="mccartney@thebeatles.com", password="paulpassword")

        # The second user with a different organization should not be able to see it
        response = self.client.get(
            "/{}/inventory/location".format(self.organization_2.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Test Location", response.content.decode())

        response = self.client.get(
            "/{}/inventory/product".format(self.organization_2.slug)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Test Product", response.content.decode())

        # Even when forcing the url to be the same as organization 1
        response = self.client.get(
            "/{}/inventory/location".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            "/{}/inventory/product".format(self.organization.slug)
        )
        self.assertEqual(response.status_code, 404)

    def test_mutations_should_only_be_seen_by_the_organization(self):
        pass
