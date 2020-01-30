from django.test import TestCase
from user.models import User
from django.template import Context, Template
from base import TestBaseWithInventory
from organization.templatetags import extra_filters
from organization.models.inventory import Product, Location, Mutation

class TestFilters(TestBaseWithInventory):
    def setUp(self):
        super(TestFilters, self).setUp()
    
    def test_filter_to_class_name(self):
        context = Context({
            'product': Product.objects.get()
        })
        template_to_render = Template(
            '{% load extra_filters %}'
            '{{ product|to_class_name }}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('Product', rendered_template)

    def test_filter_is_organization_admin_in(self):
        self.user_2 = User.objects.create_user("mccartney@thebeatles.com", "paulpassword")
        self.organization.add_user(self.user_2)

        context = Context({
            'organization': self.organization,
            'user': self.user,
            'user_2': self.user_2
        })

        template_to_render = Template(
            '{% load extra_filters %}'
            '{% if user|is_organization_admin_in:organization %}org admin{% else %}no admin{% endif %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('org admin', rendered_template)

        template_to_render = Template(
            '{% load extra_filters %}'
            '{% if user_2|is_organization_admin_in:organization %}org admin{% else %}no admin{% endif %}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('no admin', rendered_template)