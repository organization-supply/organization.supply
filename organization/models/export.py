from import_export import resources
from organization.models.inventory import Product, Location, Inventory, Mutation


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        exclude = ('organization', ) # We exclude the organization


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        exclude = ('organization', ) # We exclude the organization


class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory
        exclude = ('organization', ) # We exclude the organization


class MutationResource(resources.ModelResource):
    class Meta:
        model = Mutation
        exclude = ('organization', ) # We exclude the organization
