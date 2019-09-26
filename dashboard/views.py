from django.shortcuts import render, redirect

def index(request):
    return redirect("dashboard")

def dashboard(request):
    return render(request, 'dashboard/dashboard.html', {})

def locations(request):
    return render(request, 'dashboard/locations.html', {})

def inventory(request):
    return render(request, 'dashboard/inventory.html', {})

def mutations(request):
    return render(request, 'dashboard/mutations.html', {})

def products(request):
    return render(request, 'dashboard/products.html', {})

