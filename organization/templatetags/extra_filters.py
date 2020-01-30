from django import template

from organization.models.organization import Organization

register = template.Library()


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def is_organization_admin_in(user, organization):
    return organization.is_admin(user)
