from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from organizations.models import OrganizationUser

from user.models import User


class UserSignupForm(ModelForm):
    class Meta:
        model = User
        fields = ("email", "password")

    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
    password = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "placeholder": "Password",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )


class UserInviteForm:
    class Meta:
        model = OrganizationUser

    def save(self, *args, **kwargs):
        try:
            user = get_user_model().objects.get(
                email__iexact=self.cleaned_data["email"]
            )
        except get_user_model().MultipleObjectsReturned:
            raise forms.ValidationError(
                "This email address has been used multiple times."
            )
        except get_user_model().DoesNotExist:
            user = invitation_backend().invite_by_email(
                self.cleaned_data["email"],
                **{
                    "domain": get_current_site(self.request),
                    "organization": self.organization,
                }
            )

        return OrganizationUser.objects.create(
            user=user, organization=self.organization
        )


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name"]

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name",
                "class": "pa2 input-reset ba bg-transparent w-100",
            }
        )
    )
