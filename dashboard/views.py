from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm


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
def inventory_location(request):
    return render(
        request,
        "dashboard/inventory_location.html",
        {"inventories": Inventory.objects.all()},
    )


@login_required
def inventory_product(request):
    return render(
        request,
        "dashboard/inventory_product.html",
        {"inventories": Inventory.objects.all()},
    )


@login_required
def mutation_insert(request):
    form = MutationForm(request.POST)
    if form.is_valid():
        mutation = form.save()
        mutation.apply()
        messages.add_message(request, messages.INFO, "Transaction added!")
    return redirect("mutations")


@login_required
def mutations(request):
    return render(
        request,
        "dashboard/mutations.html",
        {
            "form": MutationForm(),
            "mutations": Mutation.objects.all().order_by("-created"),
        },
    )
