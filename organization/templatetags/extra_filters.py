from urllib.parse import urlparse, urlunparse

from django import template
from django.http import QueryDict

from organization.models.organization import Organization

register = template.Library()


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def is_organization_admin_in(user, organization):
    return organization.is_admin(user)

@register.filter
def hide_data(value, onwards_from=None):
    if not onwards_from:
        return len(value) * "x"
    else:
        return value[:onwards_from] + "...."

@register.simple_tag
def replace_query_param(url, attr, val):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_dict = QueryDict(query).copy()
    query_dict[attr] = val
    query = query_dict.urlencode()
    return urlunparse((scheme, netloc, path, params, query, fragment))


# TODO: We might want to fix this in the front-end, since it's a visual thing..
@register.filter
def get_active_plan_classes(organization, plan):
    if organization.subscription_type == plan:
        return "b--black-50 bg-near-white"
    else:
        return "b--black-10"
