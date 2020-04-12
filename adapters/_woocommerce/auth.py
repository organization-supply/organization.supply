from django.contrib import messages
from woocommerce import API
from organization.models.organization import Organization
from django import forms

class WooCommerceAuthForm(forms.Form):
    url = forms.URLField()
    consumer_key = forms.CharField(max_length=255)
    consumer_secret = forms.CharField(max_length=255)

class WooCommerceAuth():
    def __init__(self):
        self.method = "password" #authentication method (oauth or password for now)

    def authenticate(self, request):
        form = WooCommerceAuthForm(request.POST)

        if not form.is_valid():
            return False

        url = form.cleaned_data['url']
        consumer_key = form.cleaned_data['consumer_key']
        consumer_secret = form.cleaned_data['consumer_secret']
        version = "wc/v3"

        wc_api = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version=version
        )

        response = wc_api.get("products")
        if response.status_code == 200:
            self._save_authentication(request.organization, url, consumer_key, consumer_secret, version)
            messages.add_message(request, messages.SUCCESS, f"Authenticated with {form.cleaned_data['url']}")
        else:
            messages.add_message(request, messages.ERROR, f"Unable to authenticate with {form.cleaned_data['url']}")

    def is_authenticated(self):
        # pass
        # Check if the user is authenticated
        # return True
        pass

    def api(self):
        # Return an API instance that is authenticated:
        # return API(
        #     url="http://example.com",
        #     consumer_key="",
        #     consumer_secret="cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        #     version="wc/v3"
        # )
        pass

    def _save_authentication(self, organization, url, consumer_key, consumer_secret, version):
        organization.adapter_auth = {
            'url': url, 
            'consumer_key': consumer_key, 
            'consumer_secret': consumer_secret,
            'version': version
        }
        organization.save()
    
    def _get_authentication():
        # Get auth details
        pass
