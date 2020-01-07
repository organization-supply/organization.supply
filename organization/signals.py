from django.db.models.signals import post_save
from notifications.signals import notify
from organization.models.inventory import Inventory
from django.dispatch import receiver

@receiver(post_save, sender=Inventory)
def notify_listeners(sender, instance, created, **kwargs):
    print("updated", sender, instance)
    # notify.send(instance, verb='Inventory was updated!')

