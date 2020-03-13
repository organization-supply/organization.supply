from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Func, Q, Sum, Window
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import LocationAddForm, LocationEditForm
from organization.models.inventory import Inventory, Location, Mutation


@login_required
def organization_locations(request):
    locations_list = Location.objects.for_organization(request.organization)

    # Filter on tags
    if request.GET.get("tag"):
        locations_list = locations_list.filter(tags__slug=request.GET.get("tag"))

    paginator = Paginator(
        locations_list.order_by(
            request.GET.get("order_by", "-created")  # Order by creation date, or by
        ),
        100,
    )
    locations_paginator = paginator.get_page(request.GET.get("page"))
    return render(
        request, "organization/locations.html", {"locations": locations_paginator}
    )


@login_required
def organization_location_view(request, location_id):
    location = get_object_or_404(
        Location, id=location_id, organization=request.organization
    )
    inventories = Inventory.objects.for_organization(request.organization).filter(
        amount__gt=0, location=location
    )
    mutations = (
        Mutation.objects.for_organization(request.organization)
        .filter(location=location)
        .order_by("-created")
    )

    product_mutations = {}
    for product in location.available_products:
        product_mutations[product.name] = (
            Mutation.objects.for_organization(request.organization)
            .filter(
                product=product,
                location=location,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("created").asc()))
            .values("id", "cumsum", "amount", "desc", "created")
            .order_by("-created")
        )

    return render(
        request,
        "organization/location/view.html",
        {
            "location": location,
            "inventories": inventories,
            "mutations": mutations,
            "product_mutations": product_mutations,
        },
    )


@login_required
def organization_location_add(request):
    if request.method == "POST":
        form = LocationAddForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            location = form.save()
            messages.add_message(
                request, messages.INFO, "Location: {} created!".format(location.name)
            )
            return redirect(
                "organization_locations", organization=request.organization.slug
            )
    else:
        form = LocationAddForm()
        return render(request, "organization/location/add.html", {"form": form})


@login_required
def organization_location_edit(request, location_id=None):
    # Creating a new location..
    if request.method == "POST" and location_id == None:
        form = LocationEditForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location created!")
            return redirect(
                "organization_locations", organization=request.organization.slug
            )

    # Deleting a location
    elif (
        request.method == "POST"
        and location_id
        and request.POST.get("action") == "delete"
    ):
        instance = get_object_or_404(
            Location, id=location_id, organization=request.organization
        )
        instance.delete()
        messages.add_message(request, messages.INFO, "Location deleted!")
        return redirect(
            "organization_locations", organization=request.organization.slug
        )

    # Updating a location
    elif request.method == "POST" and location_id != None:
        instance = get_object_or_404(
            Location, id=location_id, organization=request.organization
        )
        form = LocationEditForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location updated!")
            return redirect(
                "organization_locations", organization=request.organization.slug
            )
        else:
            return render(request, "organization/location/edit.html", {"form": form})

    # Otherwise: get form
    elif location_id:
        instance = get_object_or_404(
            Location, id=location_id, organization=request.organization
        )
        form = LocationEditForm(instance=instance)
        return render(request, "organization/location/edit.html", {"form": form})
    else:
        form = LocationEditForm()
        return render(request, "organization/location/edit.html", {"form": form})
