import unittest

import pytest

from dashboard.models import Inventory, Location, Mutation, Product


@pytest.mark.django_db
class TestLocation(unittest.TestCase):
    def test_create_location(self):
        location = Location(name="Test Location")
        location.save()

        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.get().name, "Test Location")

    def test_delete_location(self):
        location = Location(name="Test Location")
        location.save()

        self.assertEqual(Location.objects.count(), 1)

        location.delete()

        self.assertEqual(Location.objects.count(), 0)

    def test_delete_location_with_inventory(self):
        location = Location(name="Test Location")
        location.save()

        self.assertEqual(Location.objects.count(), 1)

        product = Product(name="Test Product")
        product.save()

        self.assertEqual(Product.objects.count(), 1)

        inventory = Inventory(location=location, product=product)
        inventory.amount = 1.0
        inventory.save()

        self.assertEqual(inventory.amount, 1.0)

        # Deleting it should fail since we have inventory
        with pytest.raises(Exception) as deletion_error:
            location.delete()

        self.assertEqual(
            str(deletion_error.value),
            "We cannot delete a location if it still has inventory.",
        )

        # Removing inventory should make the location deletable
        inventory.add(-1)

        location.delete()

        self.assertEqual(Location.objects.count(), 0)


@pytest.mark.django_db
class TestProduct(unittest.TestCase):
    def test_create_product(self):
        product = Product(name="Test Product")
        product.save()

        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, "Test Product")

    def test_delete_product(self):
        pass


@pytest.mark.django_db
class TestInventory(unittest.TestCase):
    def test_create_inventory(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0)


@pytest.mark.django_db
class TestInventoryOperations(unittest.TestCase):
    def test_inventory_add(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0.0)

        inventory.add(1)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 1.0)

        self.assertEqual(len([location]), product.available_locations.count())
        self.assertEqual(location, product.available_locations[0])

        self.assertEqual(len([product]), location.available_products.count())
        self.assertEqual(product, location.available_products[0])

    def test_inventory_remove(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0.0)

        inventory.add(1)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 1.0)

        inventory.add(-1)
        inventory.refresh_from_db()

        self.assertEqual(inventory.amount, 0.0)

    def test_inventory_total(self):
        location = Location(name="Test Location")
        location.save()

        location_2 = Location(name="Test Location 2")
        location_2.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product, amount=1.0)
        inventory.save()

        inventory = Inventory(location=location_2, product=product, amount=1.0)
        inventory.save()

        self.assertEqual(product.inventory.count(), 2)
        self.assertEqual(product.inventory_total, 2)


@pytest.mark.django_db
class TestMutation(unittest.TestCase):
    def test_mutations(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0.0)

        mutation = Mutation(product=product, location=location, amount=3.0)
        mutation.save()

        inventory = Inventory.objects.get()

        self.assertEqual(inventory.amount, 3.0)

    def test_mutation_zero_amount(self):
        location = Location(name="Test Location")
        location.save()

        product = Product(name="Test Product")
        product.save()

        mutation = Mutation(product=product, location=location, amount=0.0).save()
        self.assertEqual(mutation, None)
