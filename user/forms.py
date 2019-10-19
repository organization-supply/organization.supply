from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import Form, ModelChoiceField, ModelForm, ValidationError

from dashboard.models import Location
from user.models import UserProfile


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


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["location"]
