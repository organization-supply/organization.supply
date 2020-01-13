# Custom user
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
import uuid
from typing import List

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from organization.models.notifications import notify
from organization.models.notifications import Notification


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field. But a email as primary identifier"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("name"), max_length=255, blank=True, default="")
    image = models.ImageField(
        upload_to="user/profile/", default="user/profile/default.png"
    )
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: List[str] = []

    objects = UserManager()

    @property  # Used for representation in Search
    def desc(self):
        return self.email

    @property
    def notifications_unread(self):
        return Notification.objects.filter(user=self, unread=True)

    @property
    def notifications_all(self):
        return Notification.objects.filter(user=self)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class NotificationSubscription(models.Model):
    """
    This model allows a user to subscribe to notifications to certain objects
    within an organization for updates. For example: to get a notification when
    the inventory get below a certain amount.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Content type allows us to use a generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey()
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)