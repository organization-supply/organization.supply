from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.http import Http404
from django.shortcuts import redirect
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import TokenAuthentication

from organization.models.organization import Organization
from user.models import User


class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If we are logged in, try getting the organization we currently are using
        if request.user:
            if hasattr(request.user, "organizations_organization") and view_kwargs.get(
                "organization"
            ):
                organization_slug = view_kwargs.get("organization")
                request.organization_slug = organization_slug
                view_kwargs.pop("organization", None)

                # Filter the organization on slug in URL
                organization = request.user.organizations_organization.filter(
                    slug=organization_slug
                ).first()

                # If we have a matching organization
                if organization:
                    # Get the organization object in the class that we use
                    request.organization = Organization.objects.get(
                        organization_ptr_id=organization.id
                    )

                    # In the case of a POST request, we also change the payload and
                    # add the organization, so it's available for the forms.
                    if request.method == "POST":
                        # Since the original is immutable, we make a copy
                        request.POST = request.POST.copy()
                        request.POST["organization"] = organization

                # Else, we raise
                else:
                    raise Http404
