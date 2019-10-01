from django import forms
from django.forms import ModelForm, ModelChoiceField, ValidationError
from dashboard.models import Product, Location, Mutation, Inventory


class ProductForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "pa2 input-reset ba bg-transparent w-100"}
        )
    )
    desc = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "pa2 input-reset ba bg-transparent w-100"}
        )
    )

    class Meta:
        model = Product
        fields = ["name", "desc"]


class LocationForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "pa2 input-reset ba bg-transparent w-100"}
        )
    )
    desc = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "pa2 input-reset ba bg-transparent w-100"}
        )
    )

    class Meta:
        model = Location
        fields = ["name", "desc"]


class MutationForm(ModelForm):
    product = ModelChoiceField(Product.objects.all(), empty_label=None)
    location = ModelChoiceField(Location.objects.all(), empty_label=None)
    amount = forms.FloatField(widget=forms.NumberInput(attrs={"placeholder": "Amount"}))
    desc = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Description.."})
    )

    class Meta:
        model = Mutation
        fields = ["amount", "operation", "product", "location", "desc"]

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location = cleaned_data.get("location")
        operation = cleaned_data.get("operation")
        if operation == "remove":
            inventory, created = Inventory.objects.get_or_create(
                product=product, location=location
            )
            if inventory.amount - amount < 0:
                raise ValidationError(
                    "Insufficient inventory of {} {} at {}".format(
                        amount, product.name, location.name
                    )
                )
