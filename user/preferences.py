from django import forms
from dynamic_preferences.types import FilePreference, ModelChoicePreference
from dynamic_preferences.users.registries import user_preferences_registry


@user_preferences_registry.register
class ProfileImage(FilePreference):
    name = "profile_image"
    widget = forms.FileInput(
        attrs={
            "placeholder": "Profile image",
            "class": "pa2 input-reset ba bg-transparent",
        }
    )
