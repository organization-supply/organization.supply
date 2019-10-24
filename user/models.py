from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from dashboard.models import Location


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if kwargs.get("created"):
        print("created user profile for {}".format(instance.username))
        UserProfile.objects.create(user=instance)
