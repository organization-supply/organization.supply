from base import TestBaseWithInventory
from organization.models.notifications import Notification, NotificationFactory
from user.models import User


class TestUserNotifications(TestBaseWithInventory):
    def setUp(self):
        super(TestUserNotifications, self).setUp()

    def test_user_notification_mark_as_read(self):
        NotificationFactory().for_user(self.user).send_notification(
            title="Testing a notification",
            user=self.user,
            sender=self.product,
            organization=self.product.organization,
        )
        response = self.client.get("/user/notifications")
        self.assertEqual(response.status_code, 200)

        # Having no notifications for a user should return 1 notification that is created
        self.assertIn("Testing a notification", response.content.decode())

        notification = Notification.objects.get(title="Testing a notification")

        response = self.client.get(
            "/user/notification/{}?action=mark_as_read".format(notification.id),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        notification = Notification.objects.get(title="Testing a notification")
        self.assertFalse(notification.unread)

    def test_user_notifications_mark_all_as_read(self):
        # there should be 2 notifications (1 for product, other for location)
        self.assertEqual(
            2, Notification.objects.for_user(self.user).filter(unread=True).count()
        )
        response = self.client.get("/user/notifications")
        self.assertEqual(response.status_code, 200)
        self.assertIn("New product", response.content.decode())
        self.assertIn("New location", response.content.decode())

        # Mark all as read
        response = self.client.get("/user/notifications/action?action=mark_all_as_read")
        self.assertEqual(
            0, Notification.objects.for_user(self.user).filter(unread=True).count()
        )


class TestOrganizationNotifications(TestBaseWithInventory):
    def setUp(self):
        super(TestOrganizationNotifications, self).setUp()

    def test_organization_notification_mark_as_read(self):
        response = self.client.get("/{}/notifications".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)
        self.assertIn("New product", response.content.decode())
        self.assertIn("New location", response.content.decode())

        notification = Notification.objects.for_user(self.user).for_organization(
            self.organization
        )[0]

        response = self.client.get(
            "/user/notification/{}?action=mark_as_read&organization={}".format(
                notification.id, self.organization.slug
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1,
            Notification.objects.for_user(self.user)
            .for_organization(self.organization)
            .filter(unread=True)
            .count(),
        )

    def test_organization_notifications_mark_all_as_read(self):
        response = self.client.get("/{}/notifications".format(self.organization.slug))
        self.assertEqual(response.status_code, 200)
        self.assertIn("New product", response.content.decode())
        self.assertIn("New location", response.content.decode())

        notification = Notification.objects.for_user(self.user).for_organization(
            self.organization
        )[0]

        response = self.client.get(
            "/user/notifications/action?action=mark_all_as_read&organization={}".format(
                self.organization.slug
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            0,
            Notification.objects.for_user(self.user)
            .for_organization(self.organization)
            .filter(unread=True)
            .count(),
        )
