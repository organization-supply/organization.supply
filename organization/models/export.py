import tablib
from import_export import resources
from django.db.models import QuerySet
from organization.models.inventory import Product, Location, Inventory, Mutation

class StreamingResource():
    def export_as_generator(self, queryset=None, *args, **kwargs):
        self.before_export(queryset, *args, **kwargs)
        if queryset is None:
            queryset = self.get_queryset()
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)
        # Return headers
        yield data.csv

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for obj in iterable:
            # Return subset of the data (one row)
            # This is a simple implementation to fix the tablib library which is missing returning the data as
            # generator
            data = tablib.Dataset()
            data.append(self.export_resource(obj))
            yield data.csv

        self.after_export(queryset, data, *args, **kwargs)



class ProductResource(resources.ModelResource, StreamingResource):
    class Meta:
        model = Product
        exclude = ('organization', ) # We exclude the organization


class LocationResource(resources.ModelResource, StreamingResource):
    class Meta:
        model = Location
        exclude = ('organization', ) # We exclude the organization


class InventoryResource(resources.ModelResource, StreamingResource):
    class Meta:
        model = Inventory
        exclude = ('organization', ) # We exclude the organization


class MutationResource(resources.ModelResource, StreamingResource):
    class Meta:
        model = Mutation
        exclude = ('organization', ) # We exclude the organization
