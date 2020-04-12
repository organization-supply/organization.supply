from woocommerce import API


class WooCommerceAuth():
    def __init__(self):
        pass

    def authenticate(self, url, consumer_key, consumer_secret, version="wc/v3"):
        self.version = version
        # TODO: authenticate

    def is_authenticated(self):
        # Check if the user is authenticated
        return True

    def api(self):
        # Return an API instance that is authenticated:
        return API(
            url="http://example.com",
            consumer_key="ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            consumer_secret="cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            version=self.version
        )

    def _save_authentication():
        # Save authentication details
        pass

    def _get_authentication():
        # Get auth details
        return {}
