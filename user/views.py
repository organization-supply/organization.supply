from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from dynamic_preferences.forms import global_preference_form_builder
from dynamic_preferences.users.forms import user_preference_form_builder

from user.forms import UserForm


@login_required
def settings(request):
    user_form = UserForm(instance=request.user)
    user_preference_form = user_preference_form_builder(instance=request.user)

    if request.method == "POST":
        # First and last name
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()

        # User Profile for location
        user_preference_form = user_preference_form(request.POST, request.FILES)
        if user_preference_form.is_valid():
            user_preference_form.update_preferences()

        messages.add_message(request, messages.INFO, "Settings updated!")
        return redirect("user_settings")

    return render(
        request,
        "user/settings.html",
        {"user_form": user_form, "user_preference_form": user_preference_form},
    )
