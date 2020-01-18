from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from organization.models.organization import Organization


@staff_member_required
@login_required
def deck_index(request):
    organizations = Organization.objects.all()
    return render(request, "deck/index.html", {"organizations": organizations})
