
import unittest
import pytest
from dashboard.models import Location, Product, Inventory

@pytest.mark.django_db
class TestLocation(unittest.TestCase):
    def test_create_location(self):
        location = Location(name="Test Location")
        location.save()
    
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Location.objects.get().name, "Test Location")

    def test_delete_location(self):
        pass


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
    
    def test_delete_inventory(self):
        pass