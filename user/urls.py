from django.urls import path

from organization.invite import OrganizationInvitationBackend
from user import views

urlpatterns = [
    path(
        "signup/<uuid:user_id>/<token>",
        OrganizationInvitationBackend().activate_view,
        name="invitations_register",
    ),
    path("signup", views.signup, name="user_signup"),
    path("settings", views.settings, name="user_settings"),
    path("organizations", views.organizations, name="user_organizations"),
]
