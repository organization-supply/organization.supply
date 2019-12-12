from django import template

from organization.models import Organization

register = template.Library()


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def is_organization_admin_in(user, organization):
    # If no organizaxtion is set, default to false
    if not organization:
        return False
    return organization.is_admin(user)
