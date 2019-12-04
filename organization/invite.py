import inspect

from django.contrib.auth import authenticate, login
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.urls import path
from organizations.backends.defaults import BaseBackend
from organizations.backends.tokens import RegistrationTokenGenerator

from user.forms import OrganizationAcceptForm


class OrganizationInvitationBackend(BaseBackend):
    """
    A backend for inviting new users to join the site as members of an
    organization.
    """

    notification_subject = "organizations/email/notification_subject.txt"
    notification_body = "organizations/email/notification_body.html"
    invitation_subject = "organizations/email/invitation_subject.txt"
    invitation_body = "organization/email/invitation_body.html"
    reminder_subject = "organizations/email/reminder_subject.txt"
    reminder_body = "organizations/email/reminder_body.html"
    form_class = OrganizationAcceptForm
    registration_form_template = "organization/register.html"

    def get_success_url(self):
        return reverse("user_organizations")

    def get_urls(self):
        return [
            path(
                "signup/<uuid:user_id>/<token>",
                view=self.activate_view,
                name="invitations_register",
            )
        ]

    def invite_by_email(self, email, sender=None, request=None, **kwargs):
        """Creates an inactive user with the information we know and then sends
        an invitation email for that user to complete registration.
        If your project uses email in a different way then you should make to
        extend this method as it only checks the `email` attribute for Users.
        """
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            # TODO break out user creation process
            if (
                "username"
                in inspect.getargspec(self.user_model.objects.create_user).args
            ):
                user = self.user_model.objects.create(
                    username=self.get_username(),
                    email=email,
                    password=self.user_model.objects.make_random_password(),
                )
            else:
                user = self.user_model.objects.create(
                    email=email, password=self.user_model.objects.make_random_password()
                )
            user.is_active = False
            user.save()
        self.send_invitation(user, sender, **kwargs)
        return user

    def send_invitation(self, user, sender=None, **kwargs):
        """An intermediary function for sending an invitation email that
        selects the templates, generating the token, and ensuring that the user
        has not already joined the site.
        """
        if user.is_active:
            return False
        token = self.get_token(user)
        kwargs.update({"token": token})
        self.email_message(
            user, self.invitation_subject, self.invitation_body, sender, **kwargs
        ).send()
        return True

    def send_notification(self, user, sender=None, **kwargs):
        """
        An intermediary function for sending an notification email informing
        a pre-existing, active user that they have been added to a new
        organization.
        """
        if not user.is_active:
            return False
        self.email_message(
            user, self.notification_subject, self.notification_body, sender, **kwargs
        ).send()
        return True

    def activate_view(self, request, user_id, token):
        """
        View function that activates the given User by setting `is_active` to
        true if the provided information is verified.
        """
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
        except self.user_model.DoesNotExist:
            raise Http404("Invite not found or expired")

        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404("Invite not found or expired")
        form = self.get_form(
            data=request.POST or None, files=request.FILES or None, instance=user
        )
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.save()
            self.activate_organizations(user)
            user = authenticate(
                email=form.cleaned_data["email"], password=form.cleaned_data["password"]
            )
            login(request, user)
            return redirect(self.get_success_url())
        return render(request, self.registration_form_template, {"form": form})
