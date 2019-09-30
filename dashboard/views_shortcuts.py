from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.models import Location, Inventory, Product, Mutation
from dashboard.forms import MutationForm


@login_required
def shortcut_sales(request):
    if request.method == "POST":
        mutable_form = request.POST.copy()
        mutable_form['operation'] = "remove"
        product = Product.objects.get(id=mutable_form.get('product'))
        mutable_form['desc'] = "Sold {} of {}".format(mutable_form.get('amount'), product.name)
        form = MutationForm(mutable_form)
        if form.is_valid():
            mutation = form.save()
            mutation.apply()
            messages.add_message(request, messages.INFO, "Sale recorded!")
            return redirect("dashboard")
        else:
            print(form.errors)
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
        product = Product.objects.get(id=mutable_form.get('product'))
        amount = float(mutable_form['amount'])

        mutable_form['operation'] = "remove"
        mutable_form['amount'] = amount
        mutable_form['desc'] = "Moved {} of {} to {}".format(-mutable_form.get('amount'), product.name, location_to.name)
        mutable_form['location'] = location_from.id
        form = MutationForm(mutable_form)
        if form.is_valid():
            mutation = form.save()
            mutation.apply()
            
        mutable_form['operation'] = "add"
        mutable_form['amount'] = amount
        mutable_form['desc'] = "Received {} of {} to {}".format(mutable_form.get('amount'), product.name, location_from.name)
        mutable_form['location'] = location_to.id
        form = MutationForm(mutable_form)
        if form.is_valid():
            mutation = form.save()
            mutation.apply()

        messages.add_message(request, messages.INFO, "Move recorded!")
        return redirect("dashboard")

    else:
        form = MutationForm(initial={"amount": 1.0})
        return render(request, "shortcuts/shortcut_move.html", {"form": form})