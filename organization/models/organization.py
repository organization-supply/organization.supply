import uuid

from django.db import models
from django.shortcuts import get_object_or_404
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel
from organizations.models import Organization as DjangoOrganization

CURRENCY_CHOICES = Choices(
    ("euro", "Euro (€)"),
    ("dollar", "Dollar ($)"),
    ("pound", "Pound (£)"),
    ("yen", "Yen (¥)"),
)


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
    # Stripe data
    subscription_stripe_customer_id = models.CharField(max_length=255, default="")
    subscription_stripe_checkout_session_id = models.CharField(
        max_length=255, default=""
    )
    subscription_stripe_subscription_id = models.CharField(max_length=255, default="")

    # Subscription data
    SUBSCRIPTION_CHOICES = Choices("free", "basic")
    subscription_type = StatusField(choices_name="SUBSCRIPTION_CHOICES", default="free")
    # Differs from the creation date of the organization, tracks when the subscription is changed
    subscription_date = MonitorField(monitor="subscription_type")

    # Organization data
    contact_email = models.EmailField(max_length=254, unique=True)
    description = models.TextField()
    currency = models.CharField(
        choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES.euro, max_length=255
    )

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

    def __str__(self):
        return self.name
