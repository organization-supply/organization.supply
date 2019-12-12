import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404, reverse
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel
from organizations.models import Organization as DjangoOrganization


class OrganizationManager(models.Manager):
    def __str__(self):
        return self.slug

    def for_organization(self, organization):
        # If we are receiving a string, it's most likely a slug,
        # so we do a lookup to get the organization by slug
        if type(organization) == str:
            organization = get_object_or_404(DjangoOrganization, slug=organization)
        return (
            super(OrganizationManager, self)
            .get_queryset()
            .filter(organization=organization)
        )


class Organization(DjangoOrganization, TimeStampedModel):
    SUBSCRIPTION_CHOICES = Choices("free", "plan_1", "plan_1")
    subscription_type = StatusField(choices_name="SUBSCRIPTION_CHOICES", default="free")
    subscription_date = MonitorField(
        monitor="subscription_type"
    )  # Differs from the creation date of the organization


class Location(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    desc = models.TextField(default="", blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    objects = OrganizationManager()

    @property
    def url(self):
        return reverse(
            "location_view",
            kwargs={"location_id": self.pk, "organization": self.organization.slug},
        )

    @property
    def inventory(self):
        return Inventory.objects.filter(location_id=self.id)

    @property
    def inventory_total(self):
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
        if self.inventory_total == 0 or self.inventory_total == None:
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
    objects = OrganizationManager()

    @property
    def url(self):
        return reverse(
            "product_view",
            kwargs={"product_id": self.pk, "organization": self.organization.slug},
        )

    @property
    def inventory(self):
        return Inventory.objects.filter(product_id=self.id)

    @property
    def inventory_total(self):
        return (
            Inventory.objects.filter(product=self)
            .aggregate(total=Sum("amount"))
            .get("total")
        )

    @property
    def available_locations(self):
        location_ids = Inventory.objects.filter(product_id=self.id).values_list(
            "location_id", flat=True
        )
        return Location.objects.filter(id__in=location_ids)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.inventory_total == 0 or self.inventory_total == None:
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
    objects = OrganizationManager()

    @property
    def name(self):
        return "Mutation on {}".format(str(self.created)[:10])

    @property
    def url(self):
        return reverse("mutations", kwargs={"organization": self.organization.slug})

    def apply(self):
        inventory, created = Inventory.objects.get_or_create(
            product=self.product, location=self.location, organization=self.organization
        )
        inventory.amount = inventory.amount + self.amount
        inventory.save()

    def save(self, apply=True, *args, **kwargs):
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

    objects = OrganizationManager()

    @property
    def url(self):
        return reverse(
            "inventory_locations", kwargs={"organization": self.organization.slug}
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
        self._create_mutation(amount=amount, desc=desc)
