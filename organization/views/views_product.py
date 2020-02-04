from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import ProductEditForm, ProductAddForm
from organization.models.inventory import Inventory, Mutation, Product


def organization_products(request):

    products_list = Product.objects.for_organization(request.organization).order_by(
        "-created"
    )
    paginator = Paginator(products_list, 100)
    products_paginator = paginator.get_page(request.GET.get("page"))

    return render(
        request, "organization/products.html", {"products": products_paginator}
    )


def organization_product_view(request, product_id):
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


def organization_product_add(request):
    if request.method == "POST":
        form = ProductAddForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            product = form.save()
            messages.add_message(request, messages.SUCCESS, "New product: {} created!".format(product.name))
            return redirect(
                "organization_products", organization=request.organization.slug
            )
    else:
        form = ProductAddForm()
        return render(request, "organization/product/add.html", {"form": form})

def organization_product_edit(request, product_id=None):
    # Creating a new product..
    if request.method == "POST" and product_id == None:
        form = ProductEditForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            product = form.save()
            messages.add_message(request, messages.SUCCESS, "New product: {} created!".format(product.name))
            return redirect(
                "organization_products", organization=request.organization.slug
            )

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
        return redirect("organization_products", organization=request.organization.slug)

    # Updating a product
    elif request.method == "POST" and product_id != None:
        instance = get_object_or_404(
            Product, id=product_id, organization=request.organization
        )
        form = ProductEditForm(request.POST, request.FILES or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, "Product updated!")
            return redirect(
                "organization_products", organization=request.organization.slug
            )

    # Otherwise: get form
    elif product_id:
        instance = get_object_or_404(
            Product, id=product_id, organization=request.organization
        )
        form = ProductEditForm(instance=instance)
        return render(request, "organization/product/edit.html", {"form": form})

    else:
        form = ProductEditForm()
        return render(request, "organization/product/edit.html", {"form": form})
