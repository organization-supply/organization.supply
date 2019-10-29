from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from dashboard.forms import MutationForm, ShortcutMoveForm
from dashboard.models import Inventory, Location, Mutation, Product
from user.preferences import get_default_location


@login_required
def shortcut_sales(request):
    if request.method == "POST":
        data = request.POST.copy()
        data["user"] = request.user.id
        data["operation"] = "remove"
        original_amount = data["amount"]
        product = Product.objects.get(id=data.get("product"))

        # inverse if is positive
        if float(data.get("amount")) > 0:
            data["amount"] = -float(data["amount"])

        if data["desc"]:
            data["desc"] = "Sold {} {}: {}".format(
                abs(data.get("amount")), product.name, data["desc"]
            )
        else:
            data["desc"] = "Sold {} {}".format(abs(data.get("amount")), product.name)

        form = MutationForm(
            data=data, selected_location_id=None, selected_product_id=None
        )

        if form.is_valid():
            mutation = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "{} {} sold!".format(original_amount, product.name),
            )
            return redirect("dashboard")
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )
    location = get_default_location(request)
    form = MutationForm(
        selected_product_id=request.GET.get("product"),
        selected_location_id=location,
        initial={"amount": 1, "location": location, **request.GET.dict()},
    )
    return render(request, "shortcuts/shortcut_sales.html", {"form": form})


@login_required
def shortcut_move(request):
    if request.method == "POST":
        data = request.POST.copy()
        data["user"] = request.user.id

        form = ShortcutMoveForm(
            data=data,
            user=request.user,
            selected_product_id=None,
            selected_location_id=None,
        )

        # If the form is valid:
        if form.is_valid():
            form.save()
            amount = request.POST.get("amount")
            product = Product.objects.get(id=request.POST.get("product"))
            messages.add_message(
                request, messages.SUCCESS, "{} {} moved!".format(amount, product.name)
            )
            return redirect("dashboard")

        # Otherwise add errors to messages:
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )

    # When we are just getting the form
    location = get_default_location(request)
    form = ShortcutMoveForm(
        selected_product_id=request.GET.get("product"),
        selected_location_id=request.GET.get("location_from"),
        initial={"amount": 1, "location_from": location, **request.GET.dict()},
    )
    return render(request, "shortcuts/shortcut_move.html", {"form": form})
