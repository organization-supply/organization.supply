from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from user.forms import UserForm, UserProfileForm


@login_required
def settings(request):
    user_form = UserForm()
    user_profile_form = UserProfileForm()
    return render(
        request,
        "user/settings.html",
        {"user_form": user_form, "user_profile_form": user_profile_form},
    )
