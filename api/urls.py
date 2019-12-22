from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api.views import (
    ApiAuthorize,
    LocationView,
    LocationDetailView,
    ProductView,
    ProductDetailView
)


urlpatterns = [
    path("products", ProductView.as_view()), 
    path("products/<uuid:pk>", ProductDetailView.as_view()), 
    path("locations", LocationView.as_view()), 
    path("locations/<uuid:pk>", LocationDetailView.as_view()), 
    path("auth", ApiAuthorize.as_view()), 
]
