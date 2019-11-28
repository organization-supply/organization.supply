from django import forms
from django.db.models import Q
from django.forms import Form, ModelChoiceField, ModelForm, ValidationError

from organization.models import Inventory, Location, Mutation, Organization, Product


class OrganizationForm(ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Organization name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )

    class Meta:
        model = Organization
        fields = ["name"]


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
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        ),
    )

    class Meta:
        model = Product
        fields = ["name", "desc", "organization"]


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
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        ),
    )

    class Meta:
        model = Location
        fields = ["name", "desc", "organization"]


class MutationForm(ModelForm):
    # We want to override the init, because we want to filter the
    # products available for sale based location. Or based on the
    # location we allow only the sale of certain products
    def __init__(self, organization, *args, **kwargs):
        super(MutationForm, self).__init__(*args, **kwargs)
        self.fields[
            "organization"
        ].initial = organization  # Used when submitting the form (clean method)
        self.fields["location"].queryset = Location.objects.for_organization(
            organization
        )
        self.fields["product"].queryset = Product.objects.for_organization(organization)

    class Meta:
        model = Mutation
        fields = ["amount", "product", "location", "desc", "user", "organization"]

    amount = forms.FloatField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Amount",
                "class": "lh-copy pa2 input-reset ba bg-transparent w-100",
            }
        )
    )

    product = ModelChoiceField(Product.objects.none(), empty_label=None)
    location = ModelChoiceField(Location.objects.none(), empty_label=None)

    desc = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description..",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        ),
    )

    # This validates the data and sets the right fields before saving
    # the mutation. It also checks if there is sufficient inventory
    # of a product on which we apply the mutation for the sale
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location = cleaned_data.get("location")

        # Lastly, set the user if provided:
        user = cleaned_data.get("user")
        cleaned_data["user"] = user

        # If the operation is reserved
        if cleaned_data.get("operation") == "reserved":
            return

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
    product = ModelChoiceField(Product.objects.none(), empty_label=None)
    location_from = ModelChoiceField(Location.objects.none(), empty_label=None)
    location_to = ModelChoiceField(Location.objects.none(), empty_label=None)

    # Override the init so we can filter products or locations if either
    # is supplied by the user in the GET request.
    def __init__(self, user, organization, *args, **kwargs):
        super(ShortcutMoveForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields["location_from"].queryset = Location.objects.for_organization(
            organization
        )
        self.fields["location_to"].queryset = Location.objects.for_organization(
            organization
        )
        self.fields["product"].queryset = Product.objects.for_organization(organization)

        # # Get all locations where a product is available
        # if selected_product_id:
        #     selected_product = Product.objects.get(id=selected_product_id)
        #     self.fields["location_from"].queryset = selected_product.available_locations

        # # Get all products available for a certain location
        # if selected_location_id:
        #     selected_location = Location.objects.get(id=selected_location_id)
        #     # But only if that location has any inventory
        #     if selected_location.inventory_total > 0:
        #         self.fields["product"].queryset = selected_location.available_products

        #     # We cannot move inventory to the same location
        #     self.fields["location_to"].queryset = Location.objects.filter(
        #         ~Q(id=selected_location.id)
        #     )

    # This validates the data and sets the right fields before saving
    # the mutations. It also checks if there is sufficient inventory
    # of a product on which we apply the mutations for moving
    def clean(self):
        cleaned_data = super().clean()
        amount = -cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location_from = cleaned_data.get("location_from")
        location_to = cleaned_data.get("location_to")

        # If the amount is negative, we are removing inventory
        # thus extra checks are needed, for example too see if there
        # is enough inventory to be moved.
        if float(amount) < 0.0:
            inventory, created = Inventory.objects.get_or_create(
                product=product, location=location_from
            )
            # If there is nog enough inventory, raise an error:
            if inventory.amount + amount < 0:
                raise ValidationError(
                    "Insufficient inventory of {} {} at {}".format(
                        abs(amount), product.name, location_from.name
                    )
                )

    def save(self):
        # Get all the relevant data
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        product = cleaned_data.get("product")
        location_from = cleaned_data.get("location_from")
        location_to = cleaned_data.get("location_to")

        # Create a mutation for removing inventory
        mutation_from = Mutation(
            amount=-amount,
            product=product,
            location=location_from,
            organization=product.organization,
            operation="remove",
            user=self.user,
            desc="Moved {} {} to {}".format(amount, product.name, location_to.name),
        )
        mutation_from.save()

        # Create a mutation for add inventory
        mutation_to = Mutation(
            amount=amount,
            product=product,
            location=location_to,
            organization=product.organization,
            operation="add",
            user=self.user,
            desc="Received {} {} from {}".format(
                amount, product.name, location_from.name
            ),
        )
        mutation_to.save()

        # Add the contra mutation to each so we can keep track
        # of which mutations are just moving stuff around...
        mutation_from.contra_mutation = mutation_to
        mutation_to.contra_mutation = mutation_from
        # We dont need to apply the mutation twice
        mutation_from.save(apply=False)
        mutation_to.save(apply=False)
