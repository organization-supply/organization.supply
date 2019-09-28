"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from dashboard import views
from dashboard import views_product
from dashboard import views_location

urlpatterns = [
    # Inventory urls
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("inventory", views.inventory, name="inventory"),
    path("mutations", views.mutations, name="mutations"),
    path("mutations/insert", views.mutation_insert, name="mutation_insert"),
    
    # Locations
    path("locations", views_location.locations, name="locations"),
    path("location/new", views_location.location_form, name="location_new"),
    path(
        "location/<int:location_id>", views_location.location_view, name="location_view"
    ),
    path(
        "location/<int:location_id>/edit",
        views_location.location_form,
        name="location_edit",
    ),
    path(
        "location/<int:location_id>/delete",
        views_location.location_form,
        name="location_delete",
    ),
    # Products
    path("products", views_product.products, name="products"),
    path("product/new", views_product.product_form, name="product_new"),
    path("product/<int:product_id>", views_product.product_view, name="product_view"),
    path(
        "product/<int:product_id>/edit", views_product.product_form, name="product_edit"
    ),
    path(
        "product/<int:product_id>/delete",
        views_product.product_form,
        name="product_delete",
    ),
    # User urls
    path("accounts/", include("django.contrib.auth.urls")),
    # Admin
    path("admin/", admin.site.urls),
]
