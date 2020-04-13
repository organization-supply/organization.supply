
from adapters._woocommerce.auth import WooCommerceAuth
from adapters import factory
from adapters.mapper import Mapper
from organization.models.inventory import Product

@factory.register
class WooCommerceAdapter():
    service_id = 'woocommerce'
    service_name = 'WooCommerce'
    
    def __init__(self, organization):
        self.organization = organization
        self.authentication = WooCommerceAuth()
        self.is_authenticated = self.authentication.is_authenticated(self.organization)
    
        # If we are authenticated, setup the API for the adapter to user
        if self.is_authenticated:
            self.api = self.authentication.create_api(self.organization)

    def get_mapper(self, mapper):
        mappers = {
            'products': Mapper(
                entities_local=Product.objects.for_organization(self.organization),
                entities_external=self.get_products(),
                field_id_local='id',
                field_id_external='id',
                field_mapping_id='external_service_id'
            )
        }
        return mappers.get(mapper)

    def get_products(self):
        return self.api.get("products").json()