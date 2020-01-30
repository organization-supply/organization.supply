import uuid

from django.db import models
from django.shortcuts import get_object_or_404
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

    contact_email = models.EmailField(max_length=254, unique=True)

    @property
    def stats(self):
        # TODO: fix circulair import
        # To prevent a circular import reference, we import these here
        from organization.models.inventory import Product, Location, Mutation

        return {
            "product_count": Product.objects.for_organization(self).count(),
            "location_count": Location.objects.for_organization(self).count(),
            "mutation_count": Mutation.objects.for_organization(self).count(),
        }

    # TODO: billing details here... with stripe
