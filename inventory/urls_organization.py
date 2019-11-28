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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from organizations.backends import invitation_backend

from organization import (
    views,
    views_inventory,
    views_location,
    views_product,
    views_shortcuts,
)

urlpatterns = [
    # Inventory urls
    path("dashboard", views.dashboard, name="dashboard"),
    path("settings", views.organization_settings, name="organization_settings"),
    path("search", views.search, name="search"),
    path(
        "inventory/location",
        views_inventory.inventory_location,
        name="inventory_location",
    ),
    path(
        "inventory/product", views_inventory.inventory_product, name="inventory_product"
    ),
    # Mutations
    path("mutations", views_inventory.mutations, name="mutations"),
    path("mutations/insert", views_inventory.mutation_insert, name="mutation_insert"),
    # Locations
    path("locations", views_location.locations, name="locations"),
    path("location/new", views_location.location_form, name="location_new"),
    path(
        "location/<uuid:location_id>",
        views_location.location_view,
        name="location_view",
    ),
    path(
        "location/<uuid:location_id>/edit",
        views_location.location_form,
        name="location_edit",
    ),
    path(
        "location/<uuid:location_id>/delete",
        views_location.location_form,
        name="location_delete",
    ),
    # Products
    path("products", views_product.products, name="products"),
    path("product/new", views_product.product_form, name="product_new"),
    path("product/<uuid:product_id>", views_product.product_view, name="product_view"),
    path(
        "product/<uuid:product_id>/edit",
        views_product.product_form,
        name="product_edit",
    ),
    path(
        "product/<uuid:product_id>/delete",
        views_product.product_form,
        name="product_delete",
    ),
    # Shortcuts
    path("shortcuts/sales", views_shortcuts.shortcut_sales, name="shortcut_sales"),
    path("shortcuts/move", views_shortcuts.shortcut_move, name="shortcut_move"),
    # Reservations
    path(
        "reservation/<uuid:mutation_id>",
        views_shortcuts.reservation_action,
        name="reservation_action",
    ),
]
