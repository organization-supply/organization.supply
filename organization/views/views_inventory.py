import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Func, Q, Sum, Window
from django.shortcuts import redirect, render

from organization.forms import MutationForm
from organization.models.inventory import Inventory, Location, Mutation, Product


@login_required
def organization_inventory_location(request):
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
def organization_inventory_product(request):
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
def organization_mutation_insert(request):
    mutable_form = request.POST.copy()
    mutable_form["user"] = request.user.id
    mutable_form["amount"] = mutable_form["amount"].replace(",", ".")
    mutable_form[
        "operation"
    ] = "add"  # placeholder, gets changed later during cleaning..
    form = MutationForm(data=mutable_form, organization=request.organization)
    if form.is_valid():
        mutation = form.save()
        messages.add_message(request, messages.INFO, "Transaction added!")
    else:
        messages.add_message(request, messages.ERROR, form.non_field_errors().as_text())
    return redirect("organization_mutations", organization=request.organization.slug)


@login_required
def organization_mutations(request):
    mutation_form = MutationForm(
        initial={"amount": 1.0}, organization=request.organization
    )
    mutations = Mutation.objects.for_organization(request.organization).order_by(
        "-created"
    )
    paginator = Paginator(mutations, 100)
    mutations_paginator = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "organization/mutations.html",
        {"form": mutation_form, "mutations": mutations_paginator},
    )
