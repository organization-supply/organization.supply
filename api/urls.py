from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api.views import ApiAuthorize, InventoryViewSet, LocationViewSet, ProductViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"inventory", InventoryViewSet, basename="inventory")

urlpatterns = [
    path("auth", ApiAuthorize.as_view()),
    # path("test/", include("rest_framework.urls")),
    url(r"^", include(router.urls)),
]
