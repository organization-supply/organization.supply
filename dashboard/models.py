from django.db import models
from model_utils.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField

# Create your models here.


class Location(TimeStampedModel):
    name = models.CharField(max_length=200)

    def delete(self):
        if Inventory.objects.filter(location=self).count() == 0:
            super(Location, self).delete()
        else:
            raise Exception("We cannot delete a location if it still has inventory.")


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)


class Mutation(TimeStampedModel):
    OPERATION_CHOICES = Choices("add", "remove")
    operation = StatusField(choices_name="OPERATION_CHOICES")
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()
    contra_mutation = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )


class Inventory(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    def add(self, amount: float) -> Mutation:
        # Utility function for adding product inventory, returns the mutation
        mutation = Mutation(
            operation="add", location=self.location, product=self.product, amount=amount
        )
        mutation.save()
        self.amount = self.amount + amount
        self.save()
        return mutation

    def remove(self, amount: float) -> Mutation:
        # Utility function for removing product inventory, returns the mutation
        mutation = Mutation(
            operation="remove",
            location=self.location,
            product=self.product,
            amount=amount,
        )
        mutation.save()
        self.amount = self.amount - amount
        self.save()

        # If the inventory is empty, we should delete it's record.
        if self.amount == 0:
            self.delete()

        return mutation

    def transfer(self, amount: float, other_location: Location) -> (Mutation, Mutation):
        # Try and see if we can get or create the inventory at the other location,
        # and then we try to add that amount. if that succeeds we remove inventory
        other_inventory, created = Inventory.objects.get_or_create(
            product=self.product, location=other_location
        )
        mutation_add = other_inventory.add(amount)
        mutation_remove = self.remove(amount)

        # Connect the mutation both ways
        mutation_add.contra_mutation = mutation_remove
        mutation_add.save()
        mutation_remove.contra_mutation = mutation_add
        mutation_remove.save()

        return mutation_remove, mutation_add
