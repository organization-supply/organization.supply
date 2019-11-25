import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum, Window
from django.shortcuts import redirect, render

from organization.forms import MutationForm
from organization.models import Inventory, Location, Mutation, Product


@login_required
def inventory_location(request):
    return render(
        request,
        "organization/inventory_location.html",
        {
            "inventories": Inventory.objects.for_organization(
                request.organization
            ).filter(amount__gt=0)
        },
    )


@login_required
def inventory_product(request):
    return render(
        request,
        "organization/inventory_product.html",
        {
            "inventories": Inventory.objects.for_organization(
                request.organization
            ).filter(amount__gt=0)
        },
    )


@login_required
def mutation_insert(request):
    mutable_form = request.POST.copy()
    mutable_form["user"] = request.user.id
    form = MutationForm(data=mutable_form)
    if form.is_valid():
        mutation = form.save()
        messages.add_message(request, messages.INFO, "Transaction added!")
    else:
        messages.add_message(request, messages.ERROR, form.non_field_errors().as_text())
    return redirect("mutations", organization=request.organization.slug)


@login_required
def mutations(request):
    return render(
        request,
        "organization/mutations.html",
        {
            "form": MutationForm(initial={"amount": 1.0}),
            "mutations": Mutation.objects.for_organization(
                request.organization
            ).order_by("-created"),
        },
    )
