from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import ProductForm
from organization.models.inventory import Inventory, Mutation, Product


def products(request):

    products_list = Product.objects.for_organization(request.organization).order_by(
        "-created"
    )
    paginator = Paginator(products_list, 100)
    products_paginator = paginator.get_page(request.GET.get("page"))

    return render(
        request, "organization/products.html", {"products": products_paginator}
    )


def product_view(request, product_id):
    product = get_object_or_404(
        Product, id=product_id, organization=request.organization
    )
    inventories = Inventory.objects.for_organization(request.organization).filter(
        amount__gt=0, product=product
    )
    product_total = (
        Inventory.objects.for_organization(request.organization)
        .filter(product=product)
        .aggregate(Sum("amount"))
    )
    mutations = (
        Mutation.objects.for_organization(request.organization)
        .filter(product=product)
        .order_by("-created")
    )
    return render(
        request,
        "organization/product/view.html",
        {
            "product_total": product_total,
            "product": product,
            "inventories": inventories,
            "mutations": mutations,
        },
    )


def product_form(request, product_id=None):
    # Creating a new product..
    if request.method == "POST" and product_id == None:
        form = ProductForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Product created!")
            return redirect("products", organization=request.organization.slug)

    # Deleting a product
    elif (
        request.method == "POST"
        and product_id
        and request.POST.get("action") == "delete"
    ):
        instance = get_object_or_404(
            Product, id=product_id, organization=request.organization
        )
        instance.delete()
        messages.add_message(request, messages.INFO, "Product deleted!")
        return redirect("products", organization=request.organization.slug)

    # Updating a product
    elif request.method == "POST" and product_id != None:
        instance = get_object_or_404(
            Product, id=product_id, organization=request.organization
        )
        form = ProductForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Product updated!")
            return redirect("products", organization=request.organization.slug)

    # Otherwise: get form
    elif product_id:
        instance = get_object_or_404(
            Product, id=product_id, organization=request.organization
        )
        form = ProductForm(instance=instance)
        return render(request, "organization/product/form.html", {"form": form})

    else:
        form = ProductForm()
        return render(request, "organization/product/form.html", {"form": form})
