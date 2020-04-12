from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from adapters.factory import AdapterFactory


@login_required
def organization_integration_authenticate(request, service_id):
    adapter = AdapterFactory().create_for_service(service_id)

    if request.method == "POST":
        authentication = adapter.authentication()

        # For password based auth, we check within the authenticate method
        if authentication.method == "password":
            authentication.authenticate(request)

        # For the oauth, we return a redirect url for authentication
        elif authentication.method == "oauth":
            return redirect(authentication.authenticate())

        # Other menthods are not known.. raise a 404
        else:
            raise Http404()

    return render(request, "organization/integrations/authenticate.html", {
        "adapter": adapter
    })

