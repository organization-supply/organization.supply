from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
