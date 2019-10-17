from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm, ShortcutMoveForm


@login_required
def shortcut_sales(request):
    if request.method == "POST":
        mutable_form = request.POST.copy()
        mutable_form["operation"] = "remove"
        original_amount = mutable_form["amount"]
        product = Product.objects.get(id=mutable_form.get("product"))

        # inverse if is positive
        if float(mutable_form.get("amount")) > 0:
            mutable_form["amount"] = -float(mutable_form["amount"])

        mutable_form["desc"] = "Sold {} {}".format(
            mutable_form.get("amount"), product.name
        )

        form = MutationForm(
            data=mutable_form,
            selected_location_id=None,
            selected_product_id=None,
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
            return render(request, "shortcuts/shortcut_sales.html", {"form": form})
    else:
        form = MutationForm(
            selected_product_id=request.GET.get("product"),
            selected_location_id=request.GET.get("location"),
            initial={"amount": 1, **request.GET.dict()})
        return render(request, "shortcuts/shortcut_sales.html", {"form": form})


@login_required
def shortcut_move(request):
    if request.method == "POST":
        form = ShortcutMoveForm(
            data=request.POST,
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

        # Otherwise return with errors:
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )
            return render(request, "shortcuts/shortcut_sales.html", {"form": form})

    # When we are just getting the form
    else:
        form = ShortcutMoveForm(
            selected_product_id=request.GET.get("product"),
            selected_location_id=request.GET.get("location_from"),
            initial={"amount": 1, **request.GET.dict()})
        return render(request, "shortcuts/shortcut_move.html", {"form": form})
