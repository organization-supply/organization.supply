from django.urls import path, include

from organization.invite import OrganizationInvitationBackend
from user import views
import notifications.urls
from django.contrib.auth import views as auth_views
from django.shortcuts import reverse

urlpatterns = [
    path(
        "signup/<uuid:user_id>/<token>",
        OrganizationInvitationBackend().activate_view,
        name="invitations_register",
    ),
    path("signup", views.signup, name="user_signup"),
    path("settings", views.settings, name="user_settings"),
    path("organizations", views.organizations, name="user_organizations"),
    path("notifications", include(notifications.urls, namespace='user')),
    path('password/reset', auth_views.PasswordResetView.as_view(
        html_email_template_name='registration/password_reset_email_html.html'
    ), name="password_reset"),
]
