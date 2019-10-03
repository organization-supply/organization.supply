from django.db import models
from model_utils.models import TimeStampedModel
from model_utils import Choices
from model_utils.fields import StatusField

# Create your models here.


class Location(TimeStampedModel):
    name = models.CharField(max_length=200)
    desc = models.TextField(default="")

    def delete(self):
        if Inventory.objects.filter(location=self, amount__gt=0).count() == 0:
            super(Location, self).delete()
        else:
            raise Exception("We cannot delete a location if it still has inventory.")

    @property
    def inventory(self):
        return Inventory.objects.filter(location_id=self.id)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    desc = models.TextField(default="")

    @property
    def inventory(self):
        return Inventory.objects.filter(product=self)

    def __str__(self):
        return self.name


class Mutation(TimeStampedModel):
    OPERATION_CHOICES = Choices("add", "remove")
    operation = StatusField(choices_name="OPERATION_CHOICES")
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()
    desc = models.TextField(default="")
    contra_mutation = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )

    def apply(self):
        inventory, created = Inventory.objects.get_or_create(
            product=self.product, location=self.location
        )
        if self.operation == "add":
            inventory.amount = inventory.amount + self.amount
        elif self.operation == "remove":
            inventory.amount = inventory.amount - self.amount
        inventory.save()

    def save(self, *args, **kwargs):
        self.apply()
        super(Mutation, self).save(*args, **kwargs)


class Inventory(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    def _create_mutation(self, amount: float, operation: str, desc: str = ""):
        mutation = Mutation(
            operation=operation,
            location=self.location,
            product=self.product,
            amount=amount,
            desc=desc,
        )
        return mutation.save()

    def add(self, amount: float, desc: str = "") -> Mutation:
        self._create_mutation(amount, "add", desc)

    def remove(self, amount: float, desc: str = "") -> Mutation:
        if self.amount - amount < 0:
            raise Exception("Unable to have less then 0 in inventory")
        self._create_mutation(amount, "remove", desc)

    # def transfer(
    #     self, amount: float, other_location: Location, desc: str = ""
    # ) -> (Mutation, Mutation):
    #     # Try and see if we can get or create the inventory at the other location,
    #     # and then we try to add that amount. if that succeeds we remove inventory
    #     other_inventory, created = Inventory.objects.get_or_create(
    #         product=self.product, location=other_location
    #     )
    #     mutation_add = other_inventory.add(amount, desc)
    #     mutation_remove = self.remove(amount, desc)

    #     # Connect the mutation both ways
    #     mutation_add.contra_mutation = mutation_remove
    #     mutation_add.save()
    #     mutation_remove.contra_mutation = mutation_add
    #     mutation_remove.save()
    #     return mutation_remove, mutation_add
