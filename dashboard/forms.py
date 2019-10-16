from django import forms
from django.forms import ModelForm, ModelChoiceField, ValidationError, Form
from dashboard.models import Product, Location, Mutation, Inventory


class ProductForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Product name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    desc = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )

    class Meta:
        model = Product
        fields = ["name", "desc"]


class LocationForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    desc = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )

    class Meta:
        model = Location
        fields = ["name", "desc"]


class MutationForm(ModelForm):
    amount = forms.FloatField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Amount",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    product = ModelChoiceField(Product.objects.all(), empty_label=None)
    location = ModelChoiceField(Location.objects.all(), empty_label=None)
    desc = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        ),
    )

    class Meta:
        model = Mutation
        fields = ["amount", "product", "location", "desc"]

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location = cleaned_data.get("location")

        if float(cleaned_data["amount"]) < 0.0:
            cleaned_data["operation"] = "remove"
            inventory, created = Inventory.objects.get_or_create(
                product=product, location=location
            )
            if inventory.amount + amount < 0:
                raise ValidationError(
                    "Insufficient inventory of {} {} at {}".format(
                        abs(amount), product.name, location.name
                    )
                )
        else:
            cleaned_data["operation"] = "add"


class ShortcutMoveForm(Form):
    amount = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Amount",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    product = ModelChoiceField(Product.objects.all(), empty_label=None)
    location_from = ModelChoiceField(Location.objects.all(), empty_label=None)
    location_to = ModelChoiceField(Location.objects.all(), empty_label=None)

    def clean(self):
        cleaned_data = super().clean()
        amount = -cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location_from = cleaned_data.get("location_from")
        location_to = cleaned_data.get("location_to")

        if float(amount) < 0.0:
            cleaned_data["operation"] = "remove"
            inventory, created = Inventory.objects.get_or_create(
                product=product, location=location_from
            )
            if inventory.amount + amount < 0:
                raise ValidationError(
                    "Insufficient inventory of {} {} at {}".format(
                        abs(amount), product.name, location_from.name
                    )
                )
        else:
            cleaned_data["operation"] = "add"

    def save(self):
        cleaned_data = super().clean()

        # Get data
        amount = cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location_from = cleaned_data.get("location_from")
        location_to = cleaned_data.get("location_to")

        mutation_from = Mutation(
            amount=-amount,
            product=product,
            location=location_from,
            operation="remove",
            desc="Moved {} {} to {}".format(amount, product.name, location_to.name),
        )
        mutation_from.save()

        mutation_to = Mutation(
            amount=amount,
            product=product,
            location=location_to,
            operation="remove",
            desc="Received {} {} from {}".format(
                amount, product.name, location_from.name
            ),
        )
        mutation_to.save()
