import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import get_object_or_404
from django.urls import reverse
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from model_utils.models import TimeStampedModel
from organizations.models import Organization as DjangoOrganization
from user.models import NotificationSubscription
from notifications.base.models import AbstractNotification

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

    # TODO: billing details here... with stripe
