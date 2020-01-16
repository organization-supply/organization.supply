from django.db.models.signals import post_save
from django.dispatch import receiver

from organization.models.inventory import Inventory, Location, Product
from organization.models.notifications import NotificationSubscription, notify


# Create a notification every time a new Location or Product is created within
# an organization for all users that are a member of this organization
@receiver(post_save, sender=Location)
@receiver(post_save, sender=Product)
def create_notifcation(sender, instance, created, *args, **kwargs):
    if created:
        organization_users = instance.organization.users.all()
        notification_verb = "New {}: {} was just created.".format(
            sender.__name__.lower(), instance.name
        )
        notify.send(
            sender=sender,
            user=organization_users,
            organization=instance.organization,
            verb=notification_verb,
        )


@receiver(post_save, sender=Inventory)
def inventory_notifcation(sender, instance, created, *args, **kwargs):
    product = instance.product
    location = instance.location
    amount = instance.amount
    subscriptions = NotificationSubscription.objects.all()
    for subscription in subscriptions:
        print("Should notify", subscription, amount)
        # pass
        # notify.send(
        #     sender=sender,
        #     user=subscription.user
        # )
