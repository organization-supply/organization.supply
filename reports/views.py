from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from organization.models.inventory import Product, Location, Mutation

@login_required
def reports_index(request):
    return render(request, "reports/index.html", {
        "counts": {
            "products": Product.objects.for_organization(request.organization).count(),
            "locations": Location.objects.for_organization(request.organization).count(),
            "mutations": Mutation.objects.for_organization(request.organization).count(),
            "users": request.organization.users.count(),
        }
    })
