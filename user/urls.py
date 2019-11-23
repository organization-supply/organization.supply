from django.urls import path

from user import views

urlpatterns = [
    path("signup", views.signup, name="user_signup"),
    path("settings", views.settings, name="user_settings"),
    path("organizations", views.organizations, name="user_organizations"),
]
