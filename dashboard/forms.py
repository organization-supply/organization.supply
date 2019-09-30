from django.forms import ModelForm, ModelChoiceField
from dashboard.models import Product, Location, Mutation


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["name", "desc"]


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ["name", "desc"]


class MutationForm(ModelForm):
    product = ModelChoiceField(Product.objects.all(), empty_label=None)
    location = ModelChoiceField(Location.objects.all(), empty_label=None)
    class Meta:
        model = Mutation
        fields = ["amount", "operation", "product", "location", "desc"]
