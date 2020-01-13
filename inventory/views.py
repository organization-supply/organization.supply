from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def index(request):
    return redirect("user_organizations")


@login_required
def help(request):
    return render(request, "help.html", {})
