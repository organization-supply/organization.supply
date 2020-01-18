from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404, redirect, render
from organizations.utils import create_organization
from rest_framework.authtoken.models import Token
from django.http import Http404
from organization.models.notifications import Notification, notify
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
        request, "user/settings.html", {
            "token": token.key,
            "user_form": user_form,
            "user_change_password_form": PasswordChangeForm(user=request.user)
        }
    )

@login_required
def settings_change_password(request):
    if request.method == "POST":
        change_password_form = PasswordChangeForm(request.user, request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            update_session_auth_hash(request, request.user) # Updates the current session
            messages.success(request, "Password succesfully changed!")
        else:
            errors = ",".join(map(lambda err: str(err[0]), change_password_form.errors.values()))
            messages.add_message(
                request, messages.ERROR, user_form.non_field_errors().as_text() + errors
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

    notification_filter = request.GET.get("status", "unread")
    if notification_filter == "all":
        notifications = request.user.notifications_all
    elif notification_filter == "unread":
        notifications = request.user.notifications_unread
    # We default to unread notifications
    else:
        notifications = request.user.notifications_unread

    return render(
        request,
        "notifications/notifications.html",
        {"notifications": notifications, "notification_filter": notification_filter},
    )


@login_required
def notification_action(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    print(request.GET.get("action"), notification)
    if request.GET.get("action") == "mark_as_read":
        notification.mark_as_read()

    return redirect("user_notifications")


@login_required
def organizations(request):
    return render(
        request,
        "user/organizations.html",
        {"organizations": request.user.organizations_organization.all()},
    )
