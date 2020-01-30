from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from organizations.utils import create_organization
from rest_framework.authtoken.models import Token

from organization.models.notifications import Notification, notify
from organization.models.organization import Organization
from user.forms import UserForm, UserSignupForm
from user.models import User


def signup(request):
    form = UserSignupForm(request.POST or None)
    if form.is_valid():
        # Set the password before saving...
        signup = form.save(commit=False)
        signup.password = make_password(form.cleaned_data["password"])
        signup.save()

        # Authenticate
        user = authenticate(
            username=signup.email, password=form.cleaned_data["password"]
        )
        login(request, user)

        # Redirect to organizations...
        messages.add_message(request, messages.SUCCESS, "Signup succesfull!")
        return redirect("user_organizations")
    else:
        messages.add_message(request, messages.ERROR, form.errors)
    return render(request, "registration/signup.html", {"form": form})


@login_required
def settings(request):
    if request.method == "POST":
        # First and last name
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.add_message(request, messages.INFO, "Profile updated!")
            return redirect("user_settings")
        else:
            errors = ",".join(map(lambda err: str(err[0]), user_form.errors.values()))
            messages.add_message(
                request, messages.ERROR, user_form.non_field_errors().as_text() + errors
            )
    token, _ = Token.objects.get_or_create(user=request.user)
    user_form = UserForm(instance=request.user)
    return render(
        request,
        "user/settings.html",
        {
            "token": token.key,
            "user_form": user_form,
            "user_change_password_form": PasswordChangeForm(user=request.user),
        },
    )


@login_required
def settings_change_password(request):
    if request.method == "POST":
        change_password_form = PasswordChangeForm(request.user, request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            update_session_auth_hash(
                request, request.user
            )  # Updates the current session
            messages.success(request, "Password succesfully changed!")
        else:
            errors = ",".join(
                map(lambda err: str(err[0]), change_password_form.errors.values())
            )
            messages.add_message(
                request, messages.ERROR, change_password_form.non_field_errors().as_text() + errors
            )
        return redirect("user_settings")
    else:
        raise Http404


@login_required
def notifications(request):
    if request.user.notifications.count() == 0:
        notify.send(
            request.user, user=request.user, verb="This is your first notification!"
        )

    notifications = request.user.notifications_all

    return render(
        request,
        "notifications/notifications.html",
        {"notifications": notifications},
    )


@login_required
def notification_action(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    if request.GET.get("action") == "mark_as_read":
        notification.mark_as_read()

    if request.GET.get("organization"):
        return redirect("organization_notifications", organization=request.GET.get("organization"))
        
    return redirect("user_notifications")

@login_required
def notifications_action(request):
    if request.GET.get("action") == "mark_all_as_read":
        user_notifications = Notification.objects.for_user(request.user)

        if request.GET.get("organization"):
            # Get the organization
            organization = get_object_or_404(Organization, slug=request.GET.get("organization"))

            # But only continue if the user is part of that organization.
            if request.user not in organization.users.all():
                raise Http404
            
            # Filter the user notifcations on the organization and mark as read.
            user_organization_notifications = user_notifications.for_organization(organization)
            user_organization_notifications.mark_queryset_as_read()
            return redirect("organization_notifications", organization=request.GET.get("organization"))

        else:
            user_notifications.mark_queryset_as_read()
            return redirect("user_notifications")
    else:
        raise Http404

@login_required
def organizations(request):
    return render(
        request,
        "user/organizations.html",
        {"organizations": request.user.organizations_organization.all()},
    )
