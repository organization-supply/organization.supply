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

from organization.views import (
    views_export,
    views_inventory,
    views_location,
    views_organization,
    views_product,
    views_shortcuts,
)

urlpatterns = [
    # Inventory urls
    path(
        "dashboard",
        views_organization.organization_dashboard,
        name="organization_dashboard",
    ),
    path(
        "notifications",
        views_organization.organization_notifications,
        name="organization_notifications",
    ),
    path(
        "settings",
        views_organization.organization_settings,
        name="organization_settings",
    ),
    path(
        "billing", views_organization.organization_billing, name="organization_billing"
    ),
    path("users", views_organization.organization_users, name="organization_users"),
    path(
        "integrations",
        views_organization.organization_integrations,
        name="organization_integrations",
    ),
    path("export", views_organization.organization_export, name="organization_export"),
    path(
        "export/<str:entity>",
        views_export.export_entity,
        name="organization_export_entity",
    ),
    path(
        "users/invite",
        views_organization.organization_invite_user,
        name="organization_invite_user",
    ),
    path(
        "users/remove",
        views_organization.organization_remove_user,
        name="organization_remove_user",
    ),
    path(
        "users/leave", views_organization.organization_leave, name="organization_leave"
    ),
    path("search", views_organization.organization_search, name="organization_search"),
    path(
        "inventory/location",
        views_inventory.organization_inventory_location,
        name="organization_inventory_location",
    ),
    path(
        "inventory/product",
        views_inventory.organization_inventory_product,
        name="organization_inventory_product",
    ),
    # Mutations
    path(
        "mutations",
        views_inventory.organization_mutations,
        name="organization_mutations",
    ),
    path(
        "mutations/insert",
        views_inventory.organization_mutation_insert,
        name="organization_mutation_insert",
    ),
    # Locations
    path(
        "locations",
        views_location.organization_locations,
        name="organization_locations",
    ),
    path(
        "location/new",
        views_location.organization_location_form,
        name="organization_location_new",
    ),
    path(
        "location/<uuid:location_id>",
        views_location.organization_location_view,
        name="organization_location_view",
    ),
    path(
        "location/<uuid:location_id>/edit",
        views_location.organization_location_form,
        name="organization_location_edit",
    ),
    path(
        "location/<uuid:location_id>/delete",
        views_location.organization_location_form,
        name="organization_location_delete",
    ),
    # Products
    path("products", views_product.organization_products, name="organization_products"),
    path(
        "product/new",
        views_product.organization_product_form,
        name="organization_product_new",
    ),
    path(
        "product/<uuid:product_id>",
        views_product.organization_product_view,
        name="organization_product_view",
    ),
    path(
        "product/<uuid:product_id>/edit",
        views_product.organization_product_form,
        name="organization_product_edit",
    ),
    path(
        "product/<uuid:product_id>/delete",
        views_product.organization_product_form,
        name="organization_product_delete",
    ),
    # Shortcuts
    path(
        "shortcuts/sales",
        views_shortcuts.organization_shortcut_sales,
        name="organization_shortcut_sales",
    ),
    path(
        "shortcuts/move",
        views_shortcuts.organization_shortcut_move,
        name="organization_shortcut_move",
    ),
    # Reservations
    path(
        "reservation/<uuid:mutation_id>",
        views_shortcuts.organization_reservation_action,
        name="organization_reservation_action",
    ),
    # API urls
    path("api/", include("api.urls")),
]
