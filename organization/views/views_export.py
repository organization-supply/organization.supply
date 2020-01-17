from django.contrib.auth.decorators import login_required
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from organization.models.export import (
    InventoryResource,
    LocationResource,
    MutationResource,
    ProductResource,
)
from organization.models.inventory import Inventory, Location, Mutation, Product

EXPORTABLE_ENTITIES = {
    "products": (Product, ProductResource),
    "locations": (Location, LocationResource),
    "inventory": (Inventory, InventoryResource),
    "mutations": (Mutation, MutationResource),
}


@login_required
def export_entity(request, entity):
    entity, resource = EXPORTABLE_ENTITIES.get(entity, (None, None))
    if not entity or not resource:
        raise Http404("Export entity not found")

    # We only get the objects for the current organization
    queryset = entity.objects.for_organization(request.organization)
    data = resource().export_as_generator(queryset)
    response = StreamingHttpResponse(data, content_type="csv")
    response["Content-Disposition"] = "attachment; filename={}-{}.csv".format(
        request.organization.slug, entity.__name__.lower()
    )
    return response
