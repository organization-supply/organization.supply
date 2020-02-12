from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from dal import autocomplete
from taggit.models import Tag


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

class TagsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # If not authenticated or not in an organization
        if not self.request.user or not hasattr(self.request, 'organization'):
            return Tag.objects.none()

        # Filter by organization (trough model)
        qs = Tag.objects.filter(organization_organizationtaggeditem_items__organization=self.request.organization)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs