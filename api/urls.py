from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api.views import (
    ApiAuthorize,
    LocationDetailView,
    LocationView,
    ProductDetailView,
    ProductView,
    InventoryView,
    MutationsView,
)

urlpatterns = [
    path("products", ProductView.as_view()),
    path("products/<uuid:pk>", ProductDetailView.as_view()),
    path("locations", LocationView.as_view()),
    path("locations/<uuid:pk>", LocationDetailView.as_view()),
    path("inventory", InventoryView.as_view()),
    path("mutations", MutationsView.as_view()),
    # User endpoints
    path("auth", ApiAuthorize.as_view()),
    path("notifications", ProductView.as_view()),
]
