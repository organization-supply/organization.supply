from django import forms
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference


@global_preferences_registry.register
class SiteTitle(StringPreference):
    name = "title"
    default = "My inventory"
    required = True
    widget = forms.TextInput(
        attrs={
            "placeholder": "Organization name",
            "class": "pa2 input-reset ba bg-transparent w-100",
        }
    )
