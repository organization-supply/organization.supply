from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm
import datetime


@login_required
def index(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    # today = datetime.date.today()
    # data = Mutation.objects.filter(created__lte=today).values('amount', 'created', 'operation').order_by("-created")
    # changes = list(map(lambda m: m['amount'] if m['operation'] == 'add' else -m['amount'], data))
    # dates = list(map(lambda m: m['created'], data))
    # print(list(zip(dates, changes)))
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "products": Product.objects.all(),
            "locations": Location.objects.all(),
            "inventory": Inventory.objects.filter(amount__gt=0),
        },
    )


@login_required
def inventory_location(request):
    return render(
        request,
        "dashboard/inventory_location.html",
        {"inventories": Inventory.objects.filter(amount__gt=0)},
    )


@login_required
def inventory_product(request):
    return render(
        request,
        "dashboard/inventory_product.html",
        {"inventories": Inventory.objects.filter(amount__gt=0)},
    )


@login_required
def mutation_insert(request):
    form = MutationForm(request.POST)
    if form.is_valid():
        mutation = form.save()
        messages.add_message(request, messages.INFO, "Transaction added!")
    return redirect("mutations")


@login_required
def mutations(request):
    return render(
        request,
        "dashboard/mutations.html",
        {
            "form": MutationForm(initial={"amount": 1.0}),
            "mutations": Mutation.objects.all().order_by("-created"),
        },
    )
