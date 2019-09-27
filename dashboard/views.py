from django.shortcuts import render, redirect
from dashboard.models import Location, Inventory, Product, Mutation


def index(request):
    return redirect("dashboard")


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


def inventory(request):
    return render(
        request, "dashboard/inventory.html", {"inventory": Inventory.objects.all()}
    )


def mutations(request):
    return render(
        request, "dashboard/mutations.html", {"mutations": Mutation.objects.all()}
    )
