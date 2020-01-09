
from django.db.models.signals import post_save
from organization.models.notifications import notify
from organization.models.inventory import Inventory, Product, Location
from django.dispatch import receiver

# Create a notification every time a new Location or Product is created within 
# an organization for all users that are a member of this organization
@receiver(post_save, sender=Location)
@receiver(post_save, sender=Product)
def create_notifcation(sender, instance, created, *args, **kwargs):
    if created:
        organization_users = instance.organization.users.all()
        notification_verb = "New {}: {} was just created.".format(sender.__name__.lower(), instance.name)
        notify.send(sender=sender, user=organization_users, organization=instance.organization, verb=notification_verb)
