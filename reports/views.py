from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from organization.models.inventory import Product, Location, Mutation
from django.db.models import Sum, Value

@login_required
def reports_index(request):
    products = Product.objects.for_organization(request.organization)
    
    return render(request, "reports/index.html", {
        "counts": {
            "products": products.count(),
            "locations": Location.objects.for_organization(request.organization).count(),
            "mutations": Mutation.objects.for_organization(request.organization).count(),
            "users": request.organization.users.count(),
        },
        "money": {
            "total_price_cost": products_money['total_price_cost'],
            "total_price_sale": products_money['total_price_sale'],
            "total_profit": ,
        }
    })
