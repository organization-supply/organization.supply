from base import TestBase
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

    def test_settings_change_password(self):
        response = self.client.get("/user/settings")
        self.assertEqual(response.status_code, 200)

        # Test if the user is saved
        response = self.client.post(
            "/user/settings/password/change",
            {
                "old_password": "johnpassword",
                "new_password1": "johnpasswordnew",
                "new_password2": "johnpasswordnew",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password succesfully changed", response.content.decode())

    def test_settings_change_password_invalid(self):
        # Test if the user is saved
        response = self.client.post(
            "/user/settings/password/change",
            {
                "old_password": "johnpassword",
                "new_password1": "johnpasswordnew",
                "new_password2": "johnpasswordinvalid",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The two password fields didn&#39;t match.", response.content.decode()
        )

    def test_settings_change_password_get_should_404(self):
        # Test if the user is saved
        response = self.client.get("/user/settings/password/change")
        self.assertIn("Page not found", response.content.decode())
