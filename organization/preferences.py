from django import forms
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import FilePreference, StringPreference


@global_preferences_registry.register
class OrganizationName(StringPreference):
    name = "name"
    default = "My inventory"
    required = True
    widget = forms.TextInput(
        attrs={
            "placeholder": "Organization name",
            "class": "pa2 input-reset ba bg-transparent w-100",
        }
    )


@global_preferences_registry.register
class OrganizationLogo(FilePreference):
    name = "logo"
    widget = forms.FileInput(
        attrs={
            "placeholder": "Organization logo",
            "class": "pa2 input-reset ba bg-transparent",
        }
    )
