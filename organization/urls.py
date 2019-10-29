from django.urls import path

from organization import views

urlpatterns = [path("settings", views.settings, name="organization_settings")]
