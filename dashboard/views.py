from django.shortcuts import render, redirect
from dashboard.models import Location, Inventory, Product, Mutation


def index(request):
    return redirect("dashboard")


def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "products": Product.objects.all(),
            "locations": Location.objects.all(),
            "inventory": Inventory.objects.all(),
        },
    )


def products(request):
    return render(
        request, "dashboard/products.html", {"products": Product.objects.all()}
    )


def product(request, product_id=None):
    # Creating a new product..
    if request.method == "POST" and product_id == None:
        pass

    # Updating a product
    elif request.method == "POST" and product_id != None:
        pass

    # Deleting a product
    elif request.method == "DELETE":
        pass

    # Otherwise: get form
    else:
        return render(request, "dashboard/product/form.html", {})


def locations(request):
    return render(
        request, "dashboard/locations.html", {"locations": Location.objects.all()}
    )


def location(request, location_id=None):
    # Creating a new location..
    if request.method == "POST" and location_id == None:
        pass

    # Updating a location
    elif request.method == "POST" and location_id != None:
        pass

    # Deleting a location
    elif request.method == "DELETE":
        pass

    # Otherwise: get form
    else:
        return render(request, "dashboard/location/form.html", {})


def inventory(request):
    return render(
        request, "dashboard/inventory.html", {"inventory": Inventory.objects.all()}
    )


def mutations(request):
    return render(
        request, "dashboard/mutations.html", {"mutations": Mutation.objects.all()}
    )
