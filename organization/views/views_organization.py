import datetime
from itertools import chain
import stripe

from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Q, Sum, Window
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from organization.forms import MutationForm, OrganizationForm, OrganizationInviteForm
from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.notifications import Notification
from user.models import User


# Set the strip API key
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def organization_dashboard(request):
    products = Product.objects.for_organization(request.organization)
    notifications = (
        Notification.objects.for_organization(request.organization)
        .for_user(request.user)
        .order_by("-created")[:5]
    )
    product_mutations = {}
    for product in products:
        product_mutations[product.name] = (
            Mutation.objects.for_organization(request.organization)
            .filter(
                product=product,
                contra_mutation__isnull=True,
                operation__in=["add", "remove"],
            )
            .annotate(cumsum=Window(Sum("amount"), order_by=F("created").asc()))
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
            "notifications": notifications,
        },
    )


@login_required
def organization_search(request):
    if request.GET.get("q"):
        q = request.GET.get("q")
        products = Product.objects.for_organization(request.organization).filter(
            Q(name__icontains=q) | Q(desc__icontains=q)
        )
        locations = Location.objects.for_organization(request.organization).filter(
            Q(name__icontains=q) | Q(desc__icontains=q)
        )
        users = request.organization.users.filter(
            Q(name__icontains=q) | Q(email__icontains=q)
        )
        mutations = Mutation.objects.for_organization(request.organization).filter(
            desc__icontains=q
        )

        results = list(chain(products, locations, users, mutations))
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
            messages.add_message(
                request, messages.SUCCESS, "{} created".format(organization.name)
            )

            return redirect("organization_dashboard", organization=organization.slug)
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
def organization_notifications(request):
    return render(
        request,
        "notifications/notifications.html",
        {
            "notifications": Notification.objects.for_organization(
                request.organization
            ).filter(user=request.user)
        },
    )


@login_required
def organization_export(request):
    return render(request, "organization/settings/export.html")


@login_required
def organization_settings(request):
    organization_form = OrganizationForm(
        request.POST or None, instance=request.organization
    )
    if request.method == "POST" and organization_form.is_valid():
        organization_form.save()
        messages.add_message(request, messages.SUCCESS, "Organization updated")

    return render(
        request,
        "organization/settings/settings.html",
        {"organization_form": organization_form},
    )


@login_required
def organization_billing(request):
    # Configure the Stripe data
    stripe_data = {
        "payment_method_types": ['card'],
        "subscription_data": {
            'items': [{'plan': 'plan_GwERIYxDUy7iGo'}], # Basic 20 plan..
            'default_tax_rates': ['txr_1GOLDrJ1WlH2fE9bai1LCDab'], # 21% BTW (for now)
        },
        "success_url": request.build_absolute_uri(reverse('organization_billing_change', kwargs={"organization": request.organization.slug, "status": "success"})),
        "cancel_url": request.build_absolute_uri(reverse('organization_billing_change', kwargs={"organization": request.organization.slug, "status": "cancel"}))
    }

    # If the customer is already in Stripe and connected:
    if request.organization.subscription_stripe_customer_id:
        stripe_data.update(customer=request.organization.subscription_stripe_customer_id)

    # Prefill the organization contact email if available
    elif request.organization.contact_email: 
        stripe_data.update(customer_email=request.organization.contact_email)

    # Create the stripe checkout session with the data
    stripe_session = stripe.checkout.Session.create(**stripe_data)   

    # Attach the session to the organization so we can later reference the payment
    request.organization.subscription_stripe_checkout_session_id = stripe_session.id
    request.organization.save()

    return render(request, "organization/settings/billing.html", {
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "stripe_session_id": stripe_session.id
    })

@login_required
def organization_billing_change(request, status):
    # Only continue if the payment status was a success:
    if status == "success":
        # Retrieve the session object from Stripe
        stripe_session = stripe.checkout.Session.retrieve(
                request.organization.subscription_stripe_checkout_session_id
            )

        # Update the organiation with customer & subscription data
        request.organization.subscription_stripe_customer_id = stripe_session.customer
        request.organization.subscription_stripe_subscription_id = stripe_session.subscription
        request.organization.subscription_type = "basic" # Upgrade to basic...
        request.organization.save()
        
        # Add a notification that the payment was succesfull
        messages.add_message(request, messages.INFO, "You're now on the basic plan, payment succesfull!".format())
    
    elif status == "reset":    
        # Retrieve the current subscription and update it to free
        stripe_subscription = stripe.Subscription.delete(request.organization.subscription_stripe_subscription_id)
        request.organization.subscription_stripe_subscription_id = "" # Reset the subscription id
        request.organization.subscription_type = "free" # Reset to free
        request.organization.save()
        messages.add_message(request, messages.INFO, "You're now back on the free plan!".format())

    else:
        # Add a notification that the payment did not work out. 
        messages.add_message(request, messages.ERROR, "Uh oh, something went wrong during the payment processing..".format())
    
    return redirect("organization_billing", organization=request.organization.slug)


@login_required
def organization_users(request):
    users = request.organization.users.all().order_by(
        request.GET.get("order_by", "-date_joined")  # Order by default to creation date
    )
    return render(
        request,
        "organization/settings/users.html",
        {
            "users": users,
            "organization_invite_form": OrganizationInviteForm(
                None, request.organization
            ),
        },
    )


@login_required
def organization_integrations(request):
    return render(request, "organization/settings/integrations.html", {})


@login_required
def organization_invite_user(request):
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
    return redirect("organization_users", organization=request.organization.slug)


@login_required
def organization_remove_user(request):
    # If you are not an admin, you cannot remove anyone
    if not request.organization.is_admin(request.user):
        raise Http404(
            "Unable to remove user from organization {}".format(
                request.organization.name
            )
        )

    user_to_remove = get_object_or_404(User, pk=request.GET.get("id"))

    # You cannot remove yourself
    if user_to_remove == request.user:
        messages.add_message(
            request, messages.ERROR, "You cannot remove yourself from this organization"
        )
        return redirect("organization_users", organization=request.organization.slug)

    # You cannot remove admins from this organization:
    if request.organization.is_admin(user_to_remove):
        messages.add_message(
            request, messages.ERROR, "You cannot remove an admin from an organization"
        )
        return redirect("organization_users", organization=request.organization.slug)

    request.organization.remove_user(user_to_remove)

    messages.add_message(
        request,
        messages.INFO,
        "{} removed from {}".format(user_to_remove.email, request.organization.name),
    )
    return redirect("organization_users", organization=request.organization.slug)


@login_required
def organization_leave(request):
    if request.organization.is_admin(request.user):

        messages.add_message(
            request,
            messages.ERROR,
            "You cannot leave {}  because you are an admin".format(
                request.organization.name
            ),
        )
        return redirect("user_organizations")

    else:
        request.organization.remove_user(request.user)

        messages.add_message(
            request, messages.INFO, "You left {}".format(request.organization.name)
        )
        return redirect("user_organizations")
