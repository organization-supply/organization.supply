from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api.views import (
    ApiAuthorize,
    InventoryView,
    LocationDetailView,
    LocationView,
    MutationsView,
<<<<<<< HEAD
    NotificationView,
    ProductDetailView,
    ProductView,
    UserView,
=======
    ProductDetailView,
    ProductView,
>>>>>>> 0f950ee56f22fd9aa8439224f5084f4f31196ce6
)

urlpatterns = [
    path("me", UserView.as_view()),
    path("products", ProductView.as_view()),
    path("products/<uuid:pk>", ProductDetailView.as_view()),
    path("locations", LocationView.as_view()),
    path("locations/<uuid:pk>", LocationDetailView.as_view()),
    path("inventory", InventoryView.as_view()),
    path("mutations", MutationsView.as_view()),
    # User endpoints
    path("auth", ApiAuthorize.as_view()),
    path("notifications", NotificationView.as_view()),
]
