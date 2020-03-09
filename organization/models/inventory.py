import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.urls import reverse
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from organization.models.notifications import Notification, NotificationSubscription
from organization.models.organization import Organization, OrganizationManager


class OrganizationTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # We override the save model to get the organization fo the tagged item
    # this allows us to filter tags on the through model, safely allowing
    # users to query without leaking any tagged items.
    def save(self, *args, **kwargs):
        ct = ContentType.objects.get_for_id(self.content_type_id)
        obj = ct.get_object_for_this_type(pk=self.object_id)
        self.organization = obj.organization
        super(OrganizationTaggedItem, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class Location(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    desc = models.TextField(default="", blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    image = models.ImageField(
        upload_to="organization/location/", default="organization/location/default.png"
    )

    size = models.FloatField(default=0.0)

    objects = OrganizationManager()  # Filters by organization on default

    tags = TaggableManager(through=OrganizationTaggedItem, blank=True)

    @property
    def url(self):
        return reverse(
            "organization_location_view",
            kwargs={"location_id": self.pk, "organization": self.organization.slug},
        )

    @property
    def inventory(self):
        return Inventory.objects.filter(location_id=self.id)

    @property
    def inventory_count(self):
        return (
            Inventory.objects.filter(location=self)
            .aggregate(total=Sum("amount"))
            .get("total")
        )

    @property
    def available_products(self):
        product_ids = Inventory.objects.filter(location_id=self.id).values_list(
            "product_id", flat=True
        )
        return Product.objects.filter(id__in=product_ids)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.inventory_count == 0 or self.inventory_count == None:
            # Delete all inventory objects and then the location
            Inventory.objects.filter(location=self).delete()
            super(Location, self).delete(*args, **kwargs)
        else:
            raise ValueError("We cannot delete a location if it still has inventory.")


class Product(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    desc = models.TextField(default="", blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    image = models.ImageField(
        upload_to="organization/product/", default="organization/product/default.png"
    )

    price_cost = models.FloatField(default=0.0)
    price_sale = models.FloatField(default=0.0)

    tags = TaggableManager(through=OrganizationTaggedItem, blank=True)

    objects = OrganizationManager()  # Filters by organization on default

    @property
    def data(self):
        inventory_count = Inventory.objects.filter(product=self).aggregate(inventory_count=Coalesce(Sum("amount"), 0)).get("inventory_count", 0)
        
        return {
            "price_sale": self.price_sale,
            "price_cost": self.price_cost,
            "profit": self.price_sale - self.price_cost,
            "sum_price_sale": self.price_sale * inventory_count,
            "sum_price_cost": self.price_cost * inventory_count,
            "sum_profit": (self.price_sale - self.price_cost) * inventory_count
        }

    @property
    def url(self):
        return reverse(
            "organization_product_view",
            kwargs={"product_id": self.pk, "organization": self.organization.slug},
        )

    @property
    def inventory(self):
        return Inventory.objects.filter(product_id=self.id)

    @property
    def inventory_count(self):
        return Inventory.objects.filter(product=self).aggregate(total=Sum("amount")).get("total")

    @property
    def available_locations(self):
        location_ids = Inventory.objects.filter(product_id=self.id).values_list(
            "location_id", flat=True
        )
        return Location.objects.filter(id__in=location_ids)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.inventory_count == 0 or self.inventory_count == None:
            # Delete all inventory objects and then the product
            Inventory.objects.filter(product=self).delete()
            super(Product, self).delete(*args, **kwargs)
        else:
            raise ValueError(
                "Unable to delete this product, we currently have it in inventory"
            )


class Mutation(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    OPERATION_CHOICES = Choices("add", "remove", "reserved")
    operation = StatusField(choices_name="OPERATION_CHOICES")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    desc = models.TextField(default="", blank=True)
    contra_mutation = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    objects = OrganizationManager()  # Filters by organization on default

    @property
    def name(self):
        return "Mutation on {}".format(str(self.created)[:10])

    @property
    def url(self):
        return reverse(
            "organization_mutations", kwargs={"organization": self.organization.slug}
        )

    # Applies the mutation to the inventory
    def apply(self):
        inventory, created = Inventory.objects.get_or_create(
            product=self.product, location=self.location, organization=self.organization
        )
        inventory.amount = inventory.amount + self.amount
        inventory.save()

    def save(self, apply=True, *args, **kwargs):
        # If the operation is reserved, we don't apply
        # the mutation
        if self.operation != "reserved":
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0)

    objects = OrganizationManager()  # Filters by organization on default

    notification_subscription = GenericRelation(NotificationSubscription)

    @property
    def url(self):
        return reverse(
            "organization_inventory_locations",
            kwargs={"organization": self.organization.slug},
        )

    def _create_mutation(self, amount: float, desc: str = ""):
        mutation = Mutation(
            amount=amount,
            product=self.product,
            location=self.location,
            desc=desc,
            organization=self.organization,
        )
        return mutation.save()

    def add(self, amount: float, desc: str = "") -> Mutation:
        return self._create_mutation(amount=amount, desc=desc)
