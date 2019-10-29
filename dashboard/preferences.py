from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import (
    BooleanPreference,
    ModelChoicePreference,
    StringPreference,
)
from dynamic_preferences.users.registries import user_preferences_registry

from dashboard.models import Location

# we create some section objects to link related preferences together

app = Section("app")

# We start with a global preference


@global_preferences_registry.register
class SiteTitle(StringPreference):
    section = app
    name = "title"
    default = "My inventory"
    required = True


# now we declare a per-user preference
@user_preferences_registry.register
class DefaultLocation(ModelChoicePreference):
    model = Location
    name = "default_location"
    label = "Default Location"
    default = None
    required = False


def get_default_location(request):
    if request.GET.get("location"):
        return Location.objects.get(id=request.GET.get("location"))
    elif (
        request.user
        and request.user.preferences
        and request.user.preferences.get("default_location")
    ):
        return request.user.preferences.get("default_location")
    else:
        return None
