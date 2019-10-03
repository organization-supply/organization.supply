from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from dashboard.models import Location, Product, Inventory, Mutation
import unittest
import pytest


@pytest.mark.django_db
class TestShortcuts(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )
        self.client.login(username="john", password="johnpassword")

    def test_shortcut_sale(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        inventory.add(10)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 10.0)

        response = self.client.get("/shortcuts/sales")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/shortcuts/sales",
            {"amount": 1.0, "product": product.id, "location": location.id},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "1.0 Test Product sold!")

        inventory.refresh_from_db()
        self.assertEqual(inventory.amount, 9.0)

    def test_shortcut_sale_without_inventory(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        inventory.add(1)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 1.0)

        response = self.client.get("/shortcuts/sales")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/shortcuts/sales",
            {"amount": 10.0, "product": product.id, "location": location.id},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "* Insufficient inventory of 10.0 Test Product at Test Location",
        )

        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 1.0)

    def test_shortcut_move(self):
        location = Location(name="Test Location")
        location.save()

        location_2 = Location(name="Test Location")
        location_2.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        inventory.add(10)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 10.0)

        response = self.client.get("/shortcuts/move")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/shortcuts/move",
            {
                "amount": 5.0,
                "product": product.id,
                "location": [location.id, location_2.id],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "5.0 Test Product moved!")

        inventory.refresh_from_db()
        self.assertEqual(inventory.amount, 5.0)

        location_2_inventory = Inventory.objects.get(
            product=product, location=location_2
        )
        self.assertEqual(location_2_inventory.amount, 5.0)

    def test_shortcut_move_without_inventory(self):
        location = Location(name="Test Location")
        location.save()

        location_2 = Location(name="Test Location")
        location_2.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        inventory.add(1)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 1.0)

        response = self.client.get("/shortcuts/move")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/shortcuts/move",
            {
                "amount": 5.0,
                "product": product.id,
                "location": [location.id, location_2.id],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "* Insufficient inventory of 5.0 Test Product at Test Location",
        )
