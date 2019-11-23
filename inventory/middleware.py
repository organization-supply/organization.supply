from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect


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
                )

                # If we have a matching organization
                if organization:
                    request.organization = organization[0]

                    # In the case of a POST request, we also change the payload and
                    # add the organization, so it's available for the forms.
                    if request.method == "POST":
                        # Since the original is immutable, we make a copy
                        request.POST = request.POST.copy() 
                        request.POST['organization'] = organization[0]

                # If that doesn't work, we select the only organization, if that applies
                elif request.user.organizations_organization.count() == 1:
                    request.organization = request.user.organizations_organization[0]
                    redirect("dashboard", organization=request.organization.slug)

                # If the user has multple organization, we redirect to the choose org screen:
                elif request.user.organizations_organization.count() > 1:
                    redirect("user_organizations")

                # Else, we raise
                else:
                    raise Http404