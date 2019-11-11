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
    if request.GET.get("q"):
        q = request.GET.get("q")
        results = []
        products = Product.objects.filter(Q(name__icontains=q) | Q(desc__icontains=q))
        locations = Location.objects.filter(Q(name__icontains=q) | Q(desc__icontains=q))
        mutations = Mutation.objects.filter(desc__icontains=q)

        if products:
            results += products
        if locations:
            results += locations
        if mutations:
            results += mutations

        return render(request, "dashboard/search.html", {"q": q, "results": results})
    else:
        return render(request, "dashboard/search.html", {})
