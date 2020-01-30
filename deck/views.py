from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from deck.utils import staff_or_404
from organization.models.organization import Organization


@staff_or_404
@login_required
def deck_index(request):
    organizations = Organization.objects.all()
    return render(request, "deck/index.html", {"organizations": organizations})
