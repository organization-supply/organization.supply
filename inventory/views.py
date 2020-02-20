from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from taggit.models import Tag
from organization.models.organization import Organization


@login_required
def index(request):
    return redirect("user_organizations")


@login_required
def help(request):
    return render(request, "pages/help.html", {})


@login_required
def terms(request):
    return render(request, "pages/terms.html", {})


@login_required
def privacy(request):
    return render(request, "pages/privacy.html", {})


# Error pages
def handle_400(request, *args, **kwargs):
    return render(request, "pages/error/400.html", {})


def handle_403(request, *args, **kwargs):
    return render(request, "pages/error/403.html", {})


def handle_404(request, *args, **kwargs):
    return render(request, "pages/error/404.html", {})


def handle_500(request, *args, **kwargs):
    return render(request, "pages/error/500.html", {})


class TagsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # If not authenticated or not in an organization
        if not self.request.user:
            return Tag.objects.none()

        # Get the organization
        organization_slug = self.forwarded.get("organization")
        organization = Organization.objects.get(slug=organization_slug)

        if not organization:
            return Tag.objects.none()

        if organization.slug not in list(self.request.user.organizations_organization.values_list('slug', flat=True)):
            print("not it?")
            return Tag.objects.none()

        # Filter by organization (trough model)
        qs = Tag.objects.filter(
            organization_organizationtaggeditem_items__organization=organization
        ).distinct()

        print(qs)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
