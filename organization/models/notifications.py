from django import models 
from model_utils.models import TimeStampedModel

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

    def mark_all_as_read(self, user=None):
        qset = self.unread(True)
        if user:
            qset = qset.filter(user=user)

        return qset.update(unread=False)

    def mark_all_as_unread(self, user=None):
        """Mark as unread any read messages in the current queryset.
        Optionally, filter these by user first.
        """
        qset = self.read(True)

        if user:
            qset = qset.filter(user=user)

        return qset.update(unread=True)

    def deleted(self):
        """Return only deleted items in the current queryset"""
        return self.filter(deleted=True)

    def active(self):
        """Return only active(un-deleted) items in the current queryset"""
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, user=None):
        qset = self.active()
        if user:
            qset = qset.filter(user=user)

        return qset.update(deleted=True)

    def mark_all_as_active(self, user=None):
        """Mark current queryset as active(un-deleted).
        Optionally, filter by user first.
        """
        qset = self.deleted()
        if user:
            qset = qset.filter(user=user)

        return qset.update(deleted=False)

    def mark_as_unsent(self, user=None):
        qset = self.sent()
        if user:
            qset = qset.filter(user=user)
        return qset.update(emailed=False)

    def mark_as_sent(self, user=None):
        qset = self.unsent()
        if user:
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

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
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

    data = JSONField(blank=True, null=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('-timestamp',)
        app_label = 'notifications'
        # speed up notifications count query
        index_together = ('user', 'unread')

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return u'%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago' % ctx
            return u'%(actor)s %(verb)s %(target)s %(timesince)s ago' % ctx
        if self.action_object:
            return u'%(actor)s %(verb)s %(action_object)s %(timesince)s ago' % ctx
        return u'%(actor)s %(verb)s %(timesince)s ago' % ctx

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

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
    actor = kwargs.pop('sender')
    optional_objs = [
        (kwargs.pop(opt, None), opt)
        for opt in ('target', 'action_object')
    ]
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    Notification = load_model('notifications', 'Notification')
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
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=text_type(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
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


# connect the signal
notify.connect(notify_handler, dispatch_uid='organization.notifications.notification')