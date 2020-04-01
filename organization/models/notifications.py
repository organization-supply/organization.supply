import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.dispatch import Signal
from django.utils import timezone
from django.utils.timesince import timesince as timesince_
from model_utils import Choices
from model_utils.models import TimeStampedModel

from organization.models.organization import Organization


class NotificationQuerySet(models.query.QuerySet):
    """ Notification QuerySet """
    def unread(self):
        return self.filter(unread=True)

    def read(self, include_deleted=False):
        return self.filter(unread=False)

    def for_organization(self, organization):
        return self.filter(organization=organization)

    def for_user(self, user):
        return self.filter(user=user)

    def mark_queryset_as_read(self):
        qset = self.unread()  # You can only mark unread notifications as read
        return qset.update(unread=False)


class Notification(TimeStampedModel):
    LEVELS = Choices("success", "info", "warning", "error")
    level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unread = models.BooleanField(default=True, blank=False, db_index=True)

    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    actor_content_type = models.ForeignKey(
        ContentType, related_name="notify_actor", on_delete=models.CASCADE
    )
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey("actor_content_type", "actor_object_id")

    target_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_target",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey("target_content_type", "target_object_id")

    action_object_content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="notify_action_object",
        on_delete=models.CASCADE,
    )
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey(
        "action_object_content_type", "action_object_object_id"
    )

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, db_index=True)

    # data = JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ("-timestamp",)  # sort by timestamp by default
        index_together = ("user", "unread")  # speed up notifications count query

    def timesince(self, now=None):
        return timesince_(self.timestamp, now)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()


class NotificationFactory():
    def __init__(self):
        self.users = []

    def for_user(self, user):
        self.users = [user]
        return self
    
    def for_users(self, users):
        self.users = users
        return self
    
    def send_notification(self, title, template=None, organization=None, sender=None, **kwargs):
        # TODO: warning if template is non existant?
        if template:
            description = self._render_template(template, kwargs)
        else:
            description = ""

        for user in self.users:
            self._create_notification(
                user=user,
                sender=sender,
                organization=organization,
                title=title,
                description=description
            )

    def _render_template(self, template, data):
        # TODO: Handle any template errors?
        return render_to_string(template, data)

    def _create_notification(self, title, **kwargs):
        """
        Function to create Notification instance.
        """
        # Pull the options out of kwargs
        user = kwargs.pop("user")
        organization = kwargs.pop("organization", None)
        actor = kwargs.pop("sender")
        optional_objs = [
            (kwargs.pop(opt, None), opt) for opt in ("target", "action_object")
        ]
        public = bool(kwargs.pop("public", True))
        description = kwargs.pop("description", None)
        timestamp = kwargs.pop("timestamp", timezone.now())
        level = kwargs.pop("level", Notification.LEVELS.info)

        # Check if User or Group
        # TODO implement Organization wide notifications here?
        if isinstance(user, Group):
            users = user.user_set.all()
        elif isinstance(user, (QuerySet, list)):
            users = user
        else:
            users = [user]

        new_notifications = []

        for user in users:
            newnotify = Notification(
                user=user,
                organization=organization,
                actor_content_type=ContentType.objects.get_for_model(actor),
                actor_object_id=actor.pk,
                title=title,
                public=public,
                description=description,
                timestamp=timestamp,
                level=level,
            )

            # Set optional objects
            for obj, opt in optional_objs:
                if obj is not None:
                    setattr(newnotify, "%s_object_id" % opt, obj.pk)
                    setattr(
                        newnotify,
                        "%s_content_type" % opt,
                        ContentType.objects.get_for_model(obj),
                    )

            if kwargs and EXTRA_DATA:
                newnotify.data = kwargs

            newnotify.save()
            new_notifications.append(newnotify)

        return new_notifications
            
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
