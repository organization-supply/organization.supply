from base import TestBase
from organization.models.notifications import notify
from user.models import User


class TestUserPages(TestBase):
    def setUp(self):
        super(TestUserPages, self).setUp()

    def test_signup(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/user/signup",
            {"email": "mccartney@thebeatles.com", "password": "paulpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Signup succesfull!", response.content.decode())

        response = self.client.post(
            "/user/signup",
            {"email": "mccartney@thebeatles.com", "password": "paulpassword"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "User with this Email address already exists", response.content.decode()
        )

    def test_login(self):
        response = self.client.get("/user/login/")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get("/user/logout/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 200)

        # Test if the user is saved
        response = self.client.post(
            "/user/settings", {"name": "John Lennon"}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.name, "John Lennon")

    def test_notifications(self):
        response = self.client.get("/user/notifications")
        self.assertEqual(response.status_code, 200)

        # Having no notifications for a user should return 1 notification that is created
        self.assertIn("This is your first notification!", response.content.decode())
