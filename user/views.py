from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from user.forms import UserForm, UserProfileForm
from user.models import UserProfile


@login_required
def settings(request):
    user_form = UserForm(instance=request.user)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile_form = UserProfileForm(instance=user_profile)

    if request.method == "POST":
        # First and last name
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.add_message(request, messages.INFO, "Profile updated!")

        # User Profile for location
        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        if user_profile_form.is_valid():
            user_profile_form.save()
            messages.add_message(request, messages.INFO, "Settings updated!")
        return redirect("user_settings")

    return render(
        request,
        "user/settings.html",
        {"user_form": user_form, "user_profile_form": user_profile_form},
    )
