from django import template
from urllib.parse import urlparse, urlunparse
from django.http import QueryDict
from organization.models.organization import Organization

register = template.Library()


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.filter
def is_organization_admin_in(user, organization):
    return organization.is_admin(user)

@register.simple_tag
def replace_query_param(url, attr, val):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_dict = QueryDict(query).copy()
    query_dict[attr] = val
    query = query_dict.urlencode()
    return urlunparse((scheme, netloc, path, params, query, fragment))