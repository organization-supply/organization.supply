from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render
from organizations.utils import create_organization
from rest_framework.authtoken.models import Token

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
        request, "user/settings.html", {"token": token.key, "user_form": user_form}
    )


@login_required
def organizations(request):
    return render(
        request,
        "user/organizations.html",
        {"organizations": request.user.organizations_organization.all()},
    )
