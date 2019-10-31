from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from dynamic_preferences.forms import global_preference_form_builder


@login_required
@user_passes_test(
    lambda user: user.is_superuser
)  # We only allow superuser to edit the organization
def settings(request):
    organization_preference_form = global_preference_form_builder()
    if request.method == "POST":
        organization_preference_form = organization_preference_form(
            request.POST, request.FILES
        )
        if organization_preference_form.is_valid():
            organization_preference_form.update_preferences()
            messages.add_message(request, messages.INFO, "Preferences updated!")

    users = User.objects.all()
    return render(
        request,
        "organization/settings.html",
        {"users": users, "organization_preference_form": organization_preference_form},
    )
