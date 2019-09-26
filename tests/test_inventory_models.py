
import unittest
import pytest
from dashboard.models import Location, Product, Inventory, Mutation

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

        self.assertEqual(str(deletion_error.value), 'We cannot delete a location if it still has inventory.')

        # Removing inventory should make the location deletable
        inventory.remove(1)

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
    
    def test_delete_inventory(self):
        location = Location(name="Test Location")
        location.save()
    
        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0)
        self.assertEqual(Inventory.objects.count(), 1)

        inventory.delete()
    
        self.assertEqual(Inventory.objects.count(), 0)

    def test_delete_empty_inventory(self):
        location = Location(name="Test Location")
        location.save()
    
        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.amount = 1
        inventory.save()

        self.assertEqual(inventory.amount, 1)
        self.assertEqual(Inventory.objects.count(), 1)

        inventory.remove(1)
    
        self.assertEqual(Inventory.objects.count(), 0)

@pytest.mark.django_db
class TestMutation(unittest.TestCase):
    def test_mutations(self):
        location = Location(name="Test Location")
        location.save()
    
        product = Product(name="Test Product")
        product.save()

        inventory = Inventory(location=location, product=product)
        inventory.save()

        self.assertEqual(inventory.amount, 0)

        # Adding stuff to inventory
        inventory.add(3)

        self.assertEqual(inventory.amount, 3)

        mutation_add = Mutation.objects.filter(operation="add").get()

        self.assertEqual(mutation_add.operation, 'add')
        self.assertEqual(mutation_add.product, inventory.product)
        self.assertEqual(mutation_add.location, inventory.location)
        self.assertEqual(mutation_add.amount, 3)

        # Removing stuff from inventory
        inventory.remove(1)

        self.assertEqual(inventory.amount, 2)

        mutation_remove = Mutation.objects.filter(operation="remove").get()

        self.assertEqual(mutation_remove.operation, 'remove')
        self.assertEqual(mutation_remove.product, inventory.product)
        self.assertEqual(mutation_add.location, inventory.location)
        self.assertEqual(mutation_remove.amount, 1)

        location_2 = Location(name="Test Location 2")
        location_2.save()

        # Transfer to other location, should result in 1 at each inventory
        mutation_remove_2, mutation_add_2 = inventory.transfer(1, location_2)

        # Mutations should be connected
        self.assertEqual(mutation_remove_2.contra_mutation, mutation_add_2)
        self.assertEqual(mutation_add_2.contra_mutation, mutation_remove_2)

        self.assertEqual(inventory.amount, 1)
        self.assertEqual(Mutation.objects.count(), 4)

        self.assertEqual(Inventory.objects.count(), 2)

        for inventory in Inventory.objects.all():
            self.assertEqual(inventory.amount, 1)






