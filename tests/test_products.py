from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from dashboard.models import Product


class TestProductPages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "john", "lennon@thebeatles.com", "johnpassword"
        )
        self.client.login(username="john", password="johnpassword")

    def test_products(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)

    def test_create_product(self):
        response = self.client.get("/product/new")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/product/new", {"name": "Test Product", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.get()
        response = self.client.get(
            "/product/{}".format(product.id)
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_product(self):
        response = self.client.post(
            "/product/new", {"name": "Test Product", "desc": "Test Description"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.get()

        response = self.client.post(
            "/product/{}/edit".format(product.id),
            {"name": "Updated test Product", "desc": "Updated test Description"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.get()

        self.assertEqual(product.name, "Updated test Product")
        self.assertEqual(product.desc, "Updated test Description")

    def test_delete_product(self):
        pass
