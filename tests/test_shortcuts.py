import unittest

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from dashboard.forms import MutationForm, ShortcutMoveForm
from dashboard.models import Inventory, Location, Mutation, Product


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
            {"amount": 1.0, "product": product.id, "location": location.id, "desc": ""},
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
            {
                "amount": 10.0,
                "product": product.id,
                "location": location.id,
                "desc": "",
            },
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

    def test_shortcut_sale_with_selected_product_for_location(self):
        location = Location(name="Test Location")
        location.save()

        location_2 = Location(name="Test Location")
        location_2.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product, amount=10)
        inventory.save()

        self.assertEqual(inventory.amount, 10)

        sale_form = MutationForm(selected_product_id=product.id, initial={"amount": 1})

        # We should only have 1 result and is should match location 1
        self.assertEqual(sale_form.fields["location"].queryset.count(), 1)
        self.assertEqual(sale_form.fields["location"].queryset[0].id, location.id)

    def test_shortcut_sale_with_selected_location_for_product(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        product_2 = Product(name="Test Product 2")
        product_2.save()

        inventory = Inventory(location=location, product=product, amount=10)
        inventory.save()

        self.assertEqual(inventory.amount, 10)

        sale_form = MutationForm(
            selected_location_id=location.id, initial={"amount": 1}
        )

        # We should only have 1 result and is should match product 1 (since we only have that in inventory)
        self.assertEqual(sale_form.fields["product"].queryset.count(), 1)
        self.assertEqual(sale_form.fields["product"].queryset[0].id, product.id)

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
                "location_from": location.id,
                "location_to": location_2.id,
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

        location_2 = Location(name="Test Location 2")
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
                "location_from": location.id,
                "location_to": location_2.id,
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

    def test_shortcut_move_with_selected_product_for_location(self):
        location = Location(name="Test Location")
        location.save()

        location_2 = Location(name="Test Location 2")
        location_2.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product, amount=10)
        inventory.save()

        self.assertEqual(inventory.amount, 10)

        move_form = ShortcutMoveForm(
            selected_product_id=product.id,
            selected_location_id=location.id,
            initial={"amount": 1},
        )

        # We should only have 1 result and is should match location 1
        self.assertEqual(move_form.fields["location_from"].queryset.count(), 1)
        self.assertEqual(move_form.fields["location_from"].queryset[0].id, location.id)

        self.assertEqual(move_form.fields["location_to"].queryset.count(), 1)
        self.assertEqual(move_form.fields["location_to"].queryset[0].id, location_2.id)
