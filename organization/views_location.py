from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import LocationForm
from organization.models import Inventory, Location, Mutation


def locations(request):
    locations_list = Location.objects.for_organization(request.organization).order_by(
        "-created"
    )
    paginator = Paginator(locations_list, 100)
    locations_paginator = paginator.get_page(request.GET.get("page"))
    return render(
        request, "organization/locations.html", {"locations": locations_paginator}
    )


def location_view(request, location_id):
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
    return render(
        request,
        "organization/location/view.html",
        {"location": location, "inventories": inventories, "mutations": mutations},
    )


def location_form(request, location_id=None):
    # Creating a new location..
    if request.method == "POST" and location_id == None:
        form = LocationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location created!")
            return redirect("locations", organization=request.organization.slug)

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
        return redirect("locations", organization=request.organization.slug)

    # Updating a location
    elif request.method == "POST" and location_id != None:
        instance = get_object_or_404(
            Location, id=location_id, organization=request.organization
        )
        form = LocationForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location updated!")
            return redirect("locations", organization=request.organization.slug)
        else:
            return render(request, "organization/location/form.html", {"form": form})
    # Otherwise: get form
    elif location_id:
        instance = get_object_or_404(
            Location, id=location_id, organization=request.organization
        )
        form = LocationForm(instance=instance)
        return render(request, "organization/location/form.html", {"form": form})
    else:
        form = LocationForm()
        return render(request, "organization/location/form.html", {"form": form})
