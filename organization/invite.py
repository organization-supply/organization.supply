import inspect
from email import utils as email_utils
from typing import Optional, Text

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.http import Http404
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import path, reverse
from organizations.backends.defaults import BaseBackend
from organizations.backends.tokens import RegistrationTokenGenerator

from organization.models.notifications import NotificationFactory
from user.forms import OrganizationAcceptForm
from user.models import User


class OrganizationInvitationBackend(BaseBackend):
    """
    A backend for inviting new users to join the site as members of an
    organization.
    """

    # notification_subject = "organizations/email/notification_subject.txt"
    # notification_body = "organizations/email/notification_body.txt"
    invitation_subject = "organization/email/invitation_subject.txt"
    invitation_body = "organization/email/invitation_body.txt"
    # reminder_subject = "organizations/email/reminder_subject.txt"
    # reminder_body = "organizations/email/reminder_body.txt"
    form_class = OrganizationAcceptForm
    registration_form_template = "registration/signup_invite.html"

    def get_success_url(self):
        return reverse("user_organizations")

    def invite_by_email(self, email, sender=None, request=None, **kwargs):
        """Creates an inactive user with the information we know and then sends
        an invitation email for that user to complete registration.
        If your project uses email in a different way then you should make to
        extend this method as it only checks the `email` attribute for Users.
        """
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
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

        print(user, sender, kwargs)
        # NotificationFactory().for_user(user).send_notification(
        #     title="",
        #     sender=
        # )
        # self.email_message(
        #     user, self.notification_subject, self.notification_body, sender, **kwargs
        # ).send()
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

    def email_message(
        self,
        recipient,
        subject_template: str,
        body_template: str,
        sender,
        message_class=EmailMultiAlternatives,
        **kwargs
    ):

        """
        Returns an invitation email message. This can be easily overridden.
        For instance, to send an HTML message, use the EmailMultiAlternatives message_class
        and attach the additional conent.
        """
        from_email = "{} <{}>".format(
            sender.name or sender.email,
            email_utils.parseaddr(settings.DEFAULT_FROM_EMAIL)[1],
        )
        reply_to = "{} <{}>".format(sender.name or sender.email, sender.email)

        headers = {"Reply-To": reply_to}
        kwargs.update({"sender": sender, "recipient": recipient})

        subject_template = loader.get_template(subject_template)
        body_template_txt = loader.get_template(body_template)
        body_template_html = loader.get_template(body_template.replace(".txt", ".html"))

        subject = subject_template.render(
            kwargs
        ).strip()  # Remove stray newline characters

        body = body_template_txt.render(kwargs)
        body_html = body_template_html.render(kwargs)

        email = message_class(
            subject, body, from_email, [recipient.email], headers=headers
        )
        email.attach_alternative(body_html, "text/html")

        return email
