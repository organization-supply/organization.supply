from django.db import models
from django.db.models import QuerySet
from model_utils.models import TimeStampedModel
from model_utils import Choices
from django.conf import settings
from organization.models.organization import Organization
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.dispatch import Signal
from django.contrib.auth.models import Group
from django.utils.timesince import timesince as timesince_

class NotificationQuerySet(models.query.QuerySet):
    ''' Notification QuerySet '''
    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self):
        return self.filter(unread=True)

    def read(self, include_deleted=False):
        return self.filter(unread=False)

    def mark_all_as_read(self, user):
        qset = self.unread(True) # You can only mark unread notifications as read
        qset = qset.filter(user=user)
        return qset.update(unread=False)

    def mark_all_as_unread(self, user):
        """Mark as unread any read messages in the current queryset.
        Optionally, filter these by user first.
        """
        qset = self.read(True) # You can only mark read notifications as unread
        qset = qset.filter(user=user)
        return qset.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""
        return self.filter(deleted=True)

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, user):
        qset = self.active()
        qset = qset.filter(user=user)
        return qset.update(deleted=True)

    def mark_all_as_active(self, user):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by user first.
        """
        qset = self.deleted()
        qset = qset.filter(user=user)
        return qset.update(deleted=False)

    def mark_as_unsent(self, user):
        qset = self.sent()
        qset = qset.filter(user=user)
        return qset.update(emailed=False)

    def mark_as_sent(self, user):
        qset = self.unsent()
        qset = qset.filter(user=user)
        return qset.update(emailed=True)

class Notification(TimeStampedModel):
    LEVELS = Choices('success', 'info', 'warning', 'error')
    level = models.CharField(choices=LEVELS, default=LEVELS.info, max_length=20)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unread = models.BooleanField(default=True, blank=False, db_index=True)

    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    
    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor', on_delete=models.CASCADE)
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    target_content_type = models.ForeignKey(
        ContentType,
        related_name='notify_target',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                                   related_name='notify_action_object', on_delete=models.CASCADE)
    action_object_object_id = models.CharField(max_length=255, blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False, db_index=True)

    # data = JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ('-timestamp',) # sort by timestamp by default
        index_together = ('user', 'unread') # speed up notifications count query

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

def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    user = kwargs.pop('user')
    organization = kwargs.pop('organization', None)
    actor = kwargs.pop('sender')
    optional_objs = [
        (kwargs.pop(opt, None), opt)
        for opt in ('target', 'action_object')
    ]
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    level = kwargs.pop('level', Notification.LEVELS.info)

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
            verb=verb,
            public=public,
            description=description,
            timestamp=timestamp,
            level=level
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(newnotify, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))

        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs

        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications


notify = Signal(providing_args=[  # pylint: disable=invalid-name
    'user', 'actor', 'verb', 'action_object', 'target', 'description',
    'timestamp', 'level'
])

# connect the signal
notify.connect(notify_handler, dispatch_uid='organization.notifications.notification')