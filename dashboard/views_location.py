from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from dashboard.forms import LocationForm
from dashboard.models import Inventory, Location, Mutation


def locations(request):
    return render(
        request, "dashboard/locations.html", {"locations": Location.objects.all()}
    )


def location_view(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    inventories = Inventory.objects.filter(amount__gt=0, location=location)
    mutations = Mutation.objects.filter(location=location).order_by("-created")
    return render(
        request,
        "dashboard/location/view.html",
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
            return redirect("locations")

    # Deleting a location
    elif (
        request.method == "POST"
        and location_id
        and request.POST.get("action") == "delete"
    ):
        instance = get_object_or_404(Location, id=location_id)
        instance.delete()
        messages.add_message(request, messages.INFO, "Location deleted!")
        return redirect("locations")

    # Updating a location
    elif request.method == "POST" and location_id != None:
        instance = get_object_or_404(Location, id=location_id)
        form = LocationForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location updated!")
            return redirect("locations")

    # Otherwise: get form
    elif location_id:
        instance = get_object_or_404(Location, id=location_id)
        form = LocationForm(instance=instance)
        return render(request, "dashboard/location/form.html", {"form": form})
    else:
        form = LocationForm()
        return render(request, "dashboard/location/form.html", {"form": form})
