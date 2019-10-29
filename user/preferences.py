from dynamic_preferences.types import ModelChoicePreference
from dynamic_preferences.users.registries import user_preferences_registry

from dashboard.models import Location


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
        return Location.objects.get(id=request.GET.get("location")).id
    elif (
        request.user
        and request.user.preferences
        and request.user.preferences.get("default_location")
    ):
        return request.user.preferences.get("default_location").id
    else:
        return None
