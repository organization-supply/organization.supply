import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum, Window
from django.shortcuts import redirect, render

from dashboard.forms import MutationForm
from dashboard.models import Inventory, Location, Mutation, Product


@login_required
def index(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    products = Product.objects.all()
    product_mutations = {}
    for product in products:
        product_mutations[product.name] = (
            Mutation.objects.filter(
                product=product,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("id").asc()))
            .values("id", "cumsum", "amount", "desc", "created")
            .order_by("-created")
        )

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "reservations": Mutation.objects.filter(operation="reserved").order_by(
                "-created"
            )[:5],
            "products": products,
            "locations": Location.objects.all(),
            "inventory": Inventory.objects.filter(amount__gt=0),
            "mutations": Mutation.objects.all().order_by("-created")[:5],
            "product_mutations": product_mutations,
        },
    )


@login_required
def search(request):
    if request.GET.get('q'):
        return render(request, "dashboard/search.html", {})
    else:
        return render(request, "dashboard/search.html", {})


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
    mutable_form = request.POST.copy()
    mutable_form["user"] = request.user.id
    form = MutationForm(data=mutable_form)
    print(form)
    if form.is_valid():

        mutation = form.save()
        messages.add_message(request, messages.INFO, "Transaction added!")
    else:
        messages.add_message(request, messages.ERROR, form.non_field_errors().as_text())
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
