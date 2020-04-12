from adapters.woo.auth import WooCommerceAuth
from adapters import factory

@factory.register
class WooCommerceAdapter(object):
    service_id = 'woocommerce'
    service_name = 'WooCommerce'
    authentication = WooCommerceAuth

    def __init__(self):
        pass
