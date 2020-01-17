from base import TestBaseWithInventory
from organization.models.notifications import Notification, notify
from user.models import User


class TestNotifications(TestBaseWithInventory):
    def setUp(self):
        super(TestNotifications, self).setUp()

    def test_notification_mark_as_read(self):
        notify.send(sender=self.product, user=self.user, verb="Testing a notification")
        response = self.client.get("/user/notifications")
        self.assertEqual(response.status_code, 200)

        # Having no notifications for a user should return 1 notification that is created
        self.assertIn("Testing a notification", response.content.decode())

        notification = Notification.objects.get(verb="Testing a notification")

        response = self.client.get(
            "/user/notification/{}?action=mark_as_read".format(notification.id),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        notification = Notification.objects.get(verb="Testing a notification")
        self.assertFalse(notification.unread)
