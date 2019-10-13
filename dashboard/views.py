from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm
import datetime
from django.db.models import Func, Sum, Window, F



@login_required
def index(request):
    return redirect("dashboard")


@login_required
def dashboard(request):

    products = Product.objects.all()

    mutations = {}
    for product in products:
        mutations[product.name] = Mutation.objects.filter(product=product).annotate(cumsum=Window(Sum('amount'), order_by=F('id').asc()))\
              .values('id', 'cumsum', 'amount', 'desc', 'created').order_by('-created')

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "products": products,
            "locations": Location.objects.all(),
            "inventory": Inventory.objects.filter(amount__gt=0),
            "mutations": mutations
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
