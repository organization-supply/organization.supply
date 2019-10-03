from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm


@login_required
def shortcut_sales(request):
    if request.method == "POST":
        mutable_form = request.POST.copy()
        mutable_form["operation"] = "remove"
        product = Product.objects.get(id=mutable_form.get("product"))
        mutable_form["desc"] = "Sold {} {}".format(
            mutable_form.get("amount"), product.name
        )
        form = MutationForm(mutable_form)
        if form.is_valid():
            mutation = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "{} {} sold!".format(mutable_form.get("amount"), product.name),
            )
            return redirect("dashboard")
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )
            return render(request, "shortcuts/shortcut_sales.html", {"form": form})
    else:
        form = MutationForm(initial={"amount": 1.0})
        return render(request, "shortcuts/shortcut_sales.html", {"form": form})


@login_required
def shortcut_move(request):
    if request.method == "POST":
        mutable_form = request.POST.copy()
        location_from, location_to = request.POST.getlist("location")
        location_from = Location.objects.get(id=location_from)
        location_to = Location.objects.get(id=location_to)
        product = Product.objects.get(id=mutable_form.get("product"))
        amount = float(mutable_form["amount"])

        # From
        mutable_form["operation"] = "remove"
        mutable_form["amount"] = amount
        mutable_form["desc"] = "Moved {} {} to {}".format(
            amount, product.name, location_to.name
        )
        mutable_form["location"] = location_from.id
        form_from = MutationForm(mutable_form)
        if form_from.is_valid() is False:
            messages.add_message(
                request, messages.ERROR, form_from.non_field_errors().as_text()
            )
            return render(request, "shortcuts/shortcut_move.html", {"form": form_from})

        # To
        mutable_form["operation"] = "add"
        mutable_form["amount"] = amount
        mutable_form["desc"] = "Received {} {} from {}".format(
            amount, product.name, location_from.name
        )
        mutable_form["location"] = location_to.id
        form_to = MutationForm(mutable_form)
        if not form_to.is_valid():
            messages.add_message(
                request, messages.ERROR, form_to.non_field_errors().as_text()
            )
            return render(request, "shortcuts/shortcut_move.html", {"form": form_from})

        # If all is valid, save and apply
        if form_from.is_valid() and form_to.is_valid():
            mutation_from = form_from.save()
            mutation_to = form_to.save()
            messages.add_message(
                request, messages.SUCCESS, "{} {} moved!".format(amount, product.name)
            )
            return redirect("dashboard")

    else:
        form = MutationForm(initial={"amount": 1.0})
        return render(request, "shortcuts/shortcut_move.html", {"form": form})
