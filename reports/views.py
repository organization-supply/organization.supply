from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum, Value, Window
from django.shortcuts import redirect, render
from organization.models.inventory import Location, Mutation, Product
import datetime
import pytz

@login_required
def reports_index(request):
    products = Product.objects.for_organization(request.organization)
    product_mutations = {}
    for product in products:
        product_mutations[product.name] = (
            Mutation.objects.for_organization(request.organization)
            .filter(
                product=product,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("created").asc()))
            .values("id", "cumsum", "amount", "desc", "created")
            .order_by("-created")
        )
    return render(
        request,
        "reports/index.html",
        {
            "product_mutations": product_mutations,
            "counts": {
                "products": products.count(),
                "locations": Location.objects.for_organization(
                    request.organization
                ).count(),
                "mutations": Mutation.objects.for_organization(
                    request.organization
                ).count(),
                "users": request.organization.users.count(),
            },
            "products": {
                "total_price_cost": sum(
                    product.data.get("sum_price_cost", 0) for product in products
                ),
                "total_price_sale": sum(
                    product.data.get("sum_price_sale", 0) for product in products
                ),
                "total_profit": sum(
                    product.data.get("sum_profit", 0) for product in products
                ),
            },
        },
    )


@login_required
def reports_at_date(request, date):
    at_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=pytz.utc)
    products = Product.objects.for_organization(request.organization).filter(created__lte=at_date)
    product_mutations = {}
    for product in products:
        product_mutations[product.name] = (
            Mutation.objects.for_organization(request.organization)
            .filter(
                created__lte=at_date,
                product=product,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("created").asc()))
            .values("id", "cumsum", "amount", "desc", "created")
            .order_by("-created")
        )

    total_price_cost = sum(product.inventory_at_date(at_date) * product.price_cost for product in products)
    total_price_sale = sum(product.inventory_at_date(date) * product.price_sale for product in products)
    total_profit = total_price_cost - total_price_sale

    return render(
        request,
        "reports/index.html",
        {
            "product_mutations": product_mutations,
            "counts": {
                "products": products.count(),
                "locations": Location.objects.for_organization(
                    request.organization
                ).filter(created__lte=at_date).count(),
                "mutations": Mutation.objects.for_organization(
                    request.organization
                ).filter(created__lte=at_date).count(),
                "users": request.organization.users.filter(date_joined__lte=at_date).count(),
            },
            "products": {
                "total_price_cost": total_price_cost,
                "total_price_sale": total_price_sale,
                "total_profit": total_profit,
            },
        },
    )