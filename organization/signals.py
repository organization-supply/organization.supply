from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from organization.models.inventory import Inventory, Location, Product
from organization.models.notifications import NotificationFactory


# Create a notification every time a new Location or Product is created within
# an organization for all users that are a member of this organization
@receiver(post_save, sender=Location)
def create_location_notification(sender, instance, created, *args, **kwargs):
    if created:
        organization_users = instance.organization.users.all()
        NotificationFactory().for_users(organization_users).send_notification(
            title=f"New location: {instance.name} was just created.",
            sender=sender,
            organization=instance.organization,
        )


@receiver(post_save, sender=Product)
def create_product_notification(sender, instance, created, *args, **kwargs):
    if created:
        organization_users = instance.organization.users.all()
        NotificationFactory().for_users(organization_users).send_notification(
            title=f"New product: {instance.name} was just created.",
            sender=sender,
            organization=instance.organization,
        )
