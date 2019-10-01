from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from dashboard.models import Location, Inventory
from dashboard.forms import LocationForm


def locations(request):
    return render(
        request, "dashboard/locations.html", {"locations": Location.objects.all()}
    )


def location_view(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    inventories = Inventory.objects.filter(amount__gt=0, location=location)
    return render(
        request,
        "dashboard/location/view.html",
        {"location": location, "inventories": inventories},
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

    # Updating a location
    elif request.method == "POST" and location_id != None:
        instance = get_object_or_404(Location, id=location_id)
        form = LocationForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Location updated!")
            return redirect("locations")

    # Deleting a location
    elif request.method == "DELETE":
        pass

    # Otherwise: get form
    elif location_id:
        instance = get_object_or_404(Location, id=location_id)
        form = LocationForm(instance=instance)
        return render(request, "dashboard/location/form.html", {"form": form})
    else:
        form = LocationForm()
        return render(request, "dashboard/location/form.html", {"form": form})
