
from adapters._woocommerce.auth import WooCommerceAuth
from adapters import factory
from adapters.mapper import Mapper
from organization.models.inventory import Product
from django.utils.html import strip_tags


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
                field_mapping_id='external_service_id',
                import_function=self.import_product
            )
        }
        return mappers.get(mapper)

    def get_products(self):
        response = self.api.get("products").json()
        for product in response:
            product['id'] = str(product['id'])
        return response

    def import_product(self, external_service_id):
        response = self.api.get(f"products/{external_service_id}").json()

        product = Product(
            organization=self.organization,
            name=response.get("name"),
            desc=strip_tags(response.get("description")),
            price_sale=response.get('price'),
            external_service_id=external_service_id
            # TODO: tags
        )
        product.save()
        return product