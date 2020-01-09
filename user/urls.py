
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse

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
    path("notifications", views.notifications, name="user_notifications"),
    path("notification/<int:notification_id>", views.notification_action, name="user_notification_action"),
    path(
        "password/reset", 
        auth_views.PasswordResetView.as_view(
            html_email_template_name="registration/password_reset_email_html.html"
        ),
        name="password_reset",
    ),
]
