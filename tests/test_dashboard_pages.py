from django.test import TestCase


class TestDashboardPages(TestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_dashboard(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_inventory(self):
        response = self.client.get('/inventory')
        self.assertEqual(response.status_code, 200)

    def test_products(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)

    def test_locations(self):
        response = self.client.get('/locations')
        self.assertEqual(response.status_code, 200)

    def test_mutations(self):
        response = self.client.get('/mutations')
        self.assertEqual(response.status_code, 200)

