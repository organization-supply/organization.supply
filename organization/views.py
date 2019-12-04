import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum, Window
from django.shortcuts import redirect, render

from organization.forms import MutationForm, OrganizationForm, OrganizationInviteForm
from organization.models import Inventory, Location, Mutation, Product


@login_required
def index(request):
    return redirect("user_organizations")


@login_required
def dashboard(request):
    products = Product.objects.for_organization(request.organization)
    product_mutations = {}
    for product in products:
        product_mutations[product.name] = (
            Mutation.objects.for_organization(request.organization)
            .filter(
                product=product,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("id").asc()))
            .values("id", "cumsum", "amount", "desc", "created")
            .order_by("-created")
        )

    return render(
        request,
        "organization/dashboard.html",
        {
            "reservations": Mutation.objects.for_organization(request.organization)
            .filter(operation="reserved")
            .order_by("-created")[:5],
            "products": products,
            "locations": Location.objects.for_organization(request.organization),
            "inventory": Inventory.objects.for_organization(
                request.organization
            ).filter(amount__gt=0),
            "mutations": Mutation.objects.for_organization(request.organization)
            .all()
            .order_by("-created")[:5],
            "product_mutations": product_mutations,
        },
    )


@login_required
def search(request):
    if request.GET.get("q"):
        q = request.GET.get("q")
        results = []
        products = Product.objects.for_organization(request.organization).filter(
            Q(name__icontains=q) | Q(desc__icontains=q)
        )
        locations = Location.objects.for_organization(request.organization).filter(
            Q(name__icontains=q) | Q(desc__icontains=q)
        )
        mutations = Mutation.objects.for_organization(request.organization).filter(
            desc__icontains=q
        )

        if products:
            results += products
        if locations:
            results += locations
        if mutations:
            results += mutations

        return render(request, "organization/search.html", {"q": q, "results": results})
    else:
        return render(request, "organization/search.html", {})


@login_required
def organization_create(request):
    create_organization_form = OrganizationForm(request.POST or None)
    if request.method == "POST":
        if create_organization_form.is_valid():
            organization = create_organization_form.save()
            organization.add_user(request.user, is_admin=True)
            return redirect("dashboard", organization=organization.slug)
        else:
            errors = ",".join(
                map(lambda err: str(err[0]), create_organization_form.errors.values())
            )
            messages.add_message(
                request,
                messages.ERROR,
                create_organization_form.non_field_errors().as_text() + errors,
            )

    return render(
        request,
        "organization/create.html",
        {"create_organization_form": create_organization_form},
    )


@login_required
def organization_settings(request):
    organization_invite_form = OrganizationInviteForm(
        request.POST or None, request.organization
    )
    return render(
        request,
        "organization/settings.html",
        {"organization_invite_form": organization_invite_form},
    )


@login_required
def organization_invite(request):
    if request.method == "POST":
        organization_invite_form = OrganizationInviteForm(
            request=request,
            organization=request.organization,
            data={"email": request.POST.get("email"), "is_admin": False},
        )
        if organization_invite_form.is_valid():
            organization_invite_form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "{} invited for {}".format(
                    request.POST.get("email"), request.organization.name
                ),
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                organization_invite_form.non_field_errors().as_text(),
            )
    return redirect("organization_settings", organization=request.organization.slug)
