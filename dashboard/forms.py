from django.forms import ModelForm
from dashboard.models import Product, Location, Mutation


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["name", "desc"]


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ["name", "desc"]
