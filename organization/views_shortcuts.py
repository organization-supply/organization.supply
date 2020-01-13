from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import MutationForm, ShortcutMoveForm
from organization.models.inventory import Inventory, Location, Mutation, Product


@login_required
def organization_shortcut_sales(request):
    if request.method == "POST":
        data = request.POST.copy()
        data["user"] = request.user.id
        data["amount"] = float(data["amount"])
        product = Product.objects.for_organization(request.organization).get(
            id=data.get("product")
        )

        if data.get("reserved") == "on":
            data["operation"] = "reserved"
            message = "Reserved {} {}".format(abs(data.get("amount")), product.name)
        else:
            data["operation"] = "remove"
            message = "Sold {} {}".format(abs(data.get("amount")), product.name)

        # inverse if is positive, since we are selling, its always negative
        if data.get("amount") > 0:
            data["amount"] = -data["amount"]

        # Append the description if supplied
        if data["desc"]:
            data["desc"] = "{} - {}".format(message, data["desc"])

        form = MutationForm(data=data, organization=request.organization)

        if form.is_valid():
            mutation = form.save()
            messages.add_message(request, messages.SUCCESS, message + "!")
            return redirect("organization_dashboard", organization=request.organization.slug)
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )

    form = MutationForm(
        initial={"amount": 1, **request.GET.dict()}, organization=request.organization
    )
    return render(request, "shortcuts/shortcut_sales.html", {"form": form})


@login_required
def organization_shortcut_move(request):
    if request.method == "POST":
        form = ShortcutMoveForm(
            data=request.POST, user=request.user, organization=request.organization
        )

        # If the form is valid:
        if form.is_valid():
            form.save()
            amount = request.POST.get("amount")
            product = Product.objects.for_organization(request.organization).get(
                id=request.POST.get("product")
            )
            messages.add_message(
                request, messages.SUCCESS, "{} {} moved!".format(amount, product.name)
            )
            return redirect("organization_dashboard", organization=request.organization.slug)

        # Otherwise add errors to messages:
        else:
            messages.add_message(
                request, messages.ERROR, form.non_field_errors().as_text()
            )

    # When we are just getting the form
    location = None
    form = ShortcutMoveForm(
        initial={"amount": 1, **request.GET.dict()},
        user=request.user,
        organization=request.organization,
    )
    return render(request, "shortcuts/shortcut_move.html", {"form": form})


@login_required
def organization_reservation_action(request, mutation_id):
    mutation = get_object_or_404(
        Mutation, id=mutation_id, organization=request.organization
    )
    action = request.GET.get("action")
    if action == "confirm":
        # Setting the operation to none will automatically determine the operation
        mutation.operation = None
        mutation.save()
        messages.add_message(request, messages.INFO, "Reservation confirmed!")

    elif action == "cancel":
        mutation.delete()
        messages.add_message(request, messages.INFO, "Reservation cancelled!")

    return redirect("organization_dashboard", organization=request.organization.slug)
