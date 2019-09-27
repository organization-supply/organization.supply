from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from dashboard.models import Location, Inventory, Product, Mutation


@login_required
def index(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "products": Product.objects.all(),
            "locations": Location.objects.all(),
            "inventory": Inventory.objects.all(),
        },
    )


@login_required
def inventory(request):
    return render(
        request, "dashboard/inventory.html", {"inventory": Inventory.objects.all()}
    )


@login_required
def mutations(request):
    return render(
        request, "dashboard/mutations.html", {"mutations": Mutation.objects.all()}
    )
