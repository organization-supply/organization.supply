from django.db.models import Sum
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

    @property
    def available_products(self):
        product_ids = Inventory.objects.filter(location_id=self.id).values_list(
            "product_id", flat=True
        )
        return Product.objects.filter(id__in=product_ids)

    def inventory_history(self):
        inventories = Inventory.objects.filter(location_id=self.id)
        return inventories

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    desc = models.TextField(default="")

    @property
    def inventory(self):
        return Inventory.objects.filter(product=self)

    @property
    def available_locations(self):
        location_ids = Inventory.objects.filter(product_id=self.id).values_list(
            "location_id", flat=True
        )
        return Location.objects.filter(id__in=location_ids)

    @property
    def inventory_total(self):
        return Inventory.objects.filter(product=self).aggregate(total=Sum("amount"))

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
        inventory.amount = inventory.amount + self.amount
        inventory.save()

    def save(self, apply=True, *args, **kwargs):
        if self.amount < 0:
            self.operation = "remove"
        elif self.amount > 0:
            self.operation = "add"
        elif self.amount == 0.0:
            return

        # This allows us to update mutation without applying
        # them again. Used for connecting contra mutation.
        if apply:
            self.apply()

        super(Mutation, self).save(*args, **kwargs)


class Inventory(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    def _create_mutation(self, amount: float, operation: str, desc: str = ""):
        mutation = Mutation(
            amount=amount, product=self.product, location=self.location, desc=desc
        )
        return mutation.save()

    def add(self, amount: float, desc: str = "") -> Mutation:
        self._create_mutation(amount, desc)
