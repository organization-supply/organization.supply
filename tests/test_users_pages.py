from django.test import TestCase


class TestDashboardPages(TestCase):
    def test_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)