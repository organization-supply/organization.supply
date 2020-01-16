from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def index(request):
    return redirect("user_organizations")

@login_required
def help(request):
    return render(request, "pages/help.html", {})

@login_required
def terms(request):
    return render(request, "pages/terms.html", {})

@login_required
def privacy(request):
    return render(request, "pages/privacy.html", {})
