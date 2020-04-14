from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from adapters.factory import AdapterFactory

@login_required
def organization_integration_authenticate(request, service_id):
    adapter = AdapterFactory().create(service_id, request.organization)

    if request.method == "POST":

        # For password based auth, we check within the authenticate method
        if adapter.authentication.method == "password":
            adapter.authentication.authenticate(request)

        # For the oauth, we return a redirect url for authentication
        elif adapter.authentication.method == "oauth":
            return redirect(adapter.authentication.authenticate())

        # Other menthods are not known.. raise a 404
        else:
            raise Http404()

    return render(request, "organization/integrations/authenticate.html", {
        "adapter": adapter
    })


@login_required
def organization_integration_map_entities(request, service_id, entity_name):
    adapter = AdapterFactory().create(service_id, request.organization)
    mapper = adapter.get_mapper(entity_name)

    # TODO: deal with submitting the form and parsing all the mapped items...

    return render(request, "organization/integrations/mapping.html", {
        "adapter": adapter,
        "entity_name": entity_name,
        "mapper": mapper
    })

@login_required
def organization_integration_map_entities__import(request, service_id, entity_name):
    if request.method == "POST":
        adapter = AdapterFactory().create(service_id, request.organization)
        mapper = adapter.get_mapper(entity_name)

        external_service_id = request.POST.get("external_service_id")
        imported_product = mapper.import_function(external_service_id)

        messages.add_message(request, messages.SUCCESS, f"Imported {imported_product.name} from {adapter.service_name}")
        return redirect('organization_integration_map_entities', organization=request.organization.slug, service_id=service_id, entity_name=entity_name)
    else:
        raise Http404

    
